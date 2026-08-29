/* ============ Codewright curriculum: foundation tracks ============ */
const TRACKS = [
{
  id: 'python', name: 'Python Foundations', icon: '🐍', tint: '#E4EEFA', fg: '#2A55B8',
  tagline: 'From your first print() to a working multi-file program.',
  outcomes: [
    'Write and call functions with confidence',
    'Work with lists, dicts, files and JSON',
    'Handle errors instead of crashing',
    'Design classes that model real things',
    'Structure a program across multiple files',
    'Read tracebacks and fix your own bugs',
  ],
  modules: [
    { title: 'Getting started', desc: 'What a program is, and your first runs.', lessons: [
      { id: 'py-1-1', type: 'read', title: 'How Python runs your code', min: 6, md: 'py-1-1' },
      { id: 'py-1-2', type: 'code', title: 'Your first program', min: 8, lang: 'python', md: 'py-1-2.md',
        files: [{ name: 'main.py', key: 'py-1-2.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-1-2.solution.main.py' }],
        hints: [
          'print() takes a string in quotes: print("like this").',
          'You can print two things at once: print("The answer is", 7 * 6) — or use an f-string: print(f"The answer is {7 * 6}").',
        ],
        tests: [
          { name: 'Prints Hello, world!', code: `
            assert "Hello, world!" in _out, "Expected a line: Hello, world!"` },
          { name: 'Introduces you by name', code: `
            import re
            assert re.search(r"My name is \\S+", _out), "Expected a line like: My name is Ada"` },
          { name: 'Prints the computed answer', code: `
            assert "The answer is 42" in _out, "Expected a line containing: The answer is 42"` },
          { name: 'Lets Python do the maths', code: `
            _src = open("main.py").read()
            assert ("7 * 6" in _src) or ("7*6" in _src) or ("6 * 7" in _src) or ("6*7" in _src), "Keep the multiplication 7 * 6 in the code instead of typing 42"` },
        ] },
      { id: 'py-1-3', type: 'read', title: 'Variables, types and f-strings', min: 8, md: 'py-1-3' },
      { id: 'py-1-4', type: 'code', title: 'Receipt calculator', min: 10, lang: 'python', md: 'py-1-4.md',
        files: [{ name: 'main.py', key: 'py-1-4.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-1-4.solution.main.py' }],
        hints: [
          'subtotal = price * quantity, then tax = subtotal * TAX_RATE.',
          'An f-string with two decimals: f"Subtotal: {subtotal:.2f}".',
        ],
        tests: [
          { name: 'subtotal is price × quantity', code: `
            assert abs(subtotal - 240.0) < 1e-6, f"subtotal is {subtotal!r}, expected 240.0"` },
          { name: 'tax is 25% of the subtotal', code: `
            assert abs(tax - 60.0) < 1e-6, f"tax is {tax!r}, expected 60.0"` },
          { name: 'total adds them up', code: `
            assert abs(total - 300.0) < 1e-6, f"total is {total!r}, expected 300.0"` },
          { name: 'All four receipt lines, formatted', code: `
            _want = ["Item: Wiper blades", "Subtotal: 240.00", "Tax: 60.00", "Total: 300.00"]
            _have = [_l.strip() for _l in _out.splitlines() if _l.strip()]
            for _line in _want:
                if _line in _out:
                    continue
                _label = _line.split(":")[0]
                _near = next((_h for _h in _have if _h.startswith(_label + ":")), None)
                if _near:
                    raise AssertionError(
                        f"Printed {_near!r} but expected {_line!r} \u2014 money needs two "
                        f"decimals, so format it with :.2f inside the f-string.")
                raise AssertionError(f"Nothing printed for {_label!r}. Expected: {_line}")` },
        ] },
      { id: 'py-1-5', type: 'quiz', title: 'Check: the basics', min: 5, questions: [
        { q: 'What does `print(3 + 4 * 2)` show?', opts: ['14', '11', '342', 'An error'], a: 1, why: 'Multiplication binds tighter than addition: 4 * 2 first, then + 3.' },
        { q: 'Which of these is a valid variable name?', opts: ['2fast', 'total-price', 'total_price', 'class'], a: 2, why: 'Names cannot start with a digit or contain a dash, and class is a reserved word.' },
        { q: 'What is `type(3.0)`?', opts: ['int', 'float', 'str', 'number'], a: 1, why: 'A decimal point makes it a float, even when the fraction is zero.' },
        { q: 'What does `"5" + "5"` evaluate to?', opts: ['10', '"55"', 'An error', '"10"'], a: 1, why: 'Both values are strings, so + joins them.' },
        { q: 'What does `10 % 3` give?', opts: ['3', '1', '3.33', '0'], a: 1, why: '% is the remainder after division: 10 = 3·3 + 1.' },
        { q: 'With `name = "ada"`, what does `print(f"Hi {name.upper()}!")` show?', opts: ['Hi ada!', 'Hi ADA!', 'Hi {name.upper()}!', 'An error'], a: 1, why: 'f-strings evaluate the expression inside the braces before inserting it.' },
      ] },
    ] },
    { title: 'Control flow', desc: 'Decisions and repetition.', lessons: [
      { id: 'py-2-1', type: 'read', title: 'Making decisions and repeating work', min: 9, md: 'py-2-1' },
      { id: 'py-2-2', type: 'code', title: 'FizzBuzz, the honest way', min: 12, lang: 'python', md: 'py-2-2.md',
        files: [{ name: 'main.py', key: 'py-2-2.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-2-2.solution.main.py' }],
        hints: [
          'Loop with for i in range(1, n + 1) so n itself is included.',
          'Check the "both" case first: i % 15 == 0 (or i % 3 == 0 and i % 5 == 0).',
          'str(i) turns the number into a string before appending.',
        ],
        tests: [
          { name: 'Handles 1..15 correctly', code: `
            _r = fizzbuzz(15)
            _e = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
            assert _r == _e, f"fizzbuzz(15) returned {_r!r}"` },
          { name: 'Returns strings, not numbers', code: `
            assert all(isinstance(x, str) for x in fizzbuzz(10)), "Every element should be a string — use str(i)"` },
          { name: 'Empty list for n = 0', code: `
            assert fizzbuzz(0) == [], f"fizzbuzz(0) returned {fizzbuzz(0)!r}"` },
          { name: 'Includes n itself', code: `
            assert fizzbuzz(3)[-1] == "Fizz", "The range must include n — use range(1, n + 1)"` },
        ] },
      { id: 'py-2-3', type: 'code', title: 'Grading loop', min: 12, lang: 'python', md: 'py-2-3.md',
        files: [{ name: 'main.py', key: 'py-2-3.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-2-3.solution.main.py' }],
        hints: [
          'Check the highest boundary first: if score >= 90 ... elif score >= 80 ...',
          'Start count_grades with all five keys at 0, then add 1 to counts[letter_grade(score)] per score.',
        ],
        tests: [
          { name: 'Boundary values land right', code: `
            _r = [letter_grade(s) for s in [95, 90, 89.9, 80, 72, 60, 59.9, 0]]
            assert _r == ["A", "A", "B", "B", "C", "D", "F", "F"], f"Got {_r!r} — check the boundaries 90, 80, 70, 60"` },
          { name: 'count_grades counts per letter', code: `
            _r = count_grades([95, 82, 71, 64, 33, 88])
            assert _r == {"A": 1, "B": 2, "C": 1, "D": 1, "F": 1}, f"Got {_r!r}"` },
          { name: 'All five keys, even at zero', code: `
            assert count_grades([]) == {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}, "An empty list should still return all five letters with count 0"` },
        ] },
      { id: 'py-2-4', type: 'quiz', title: 'Check: control flow', min: 5, questions: [
        { q: 'How many times does the body of `for i in range(3):` run?', opts: ['2', '3', '4', 'Forever'], a: 1, why: 'range(3) yields 0, 1, 2 — three values.' },
        { q: 'What does `range(2, 10, 3)` produce?', opts: ['2, 5, 8', '2, 4, 6, 8', '3, 6, 9', '2, 5, 8, 11'], a: 0, why: 'Start at 2, step by 3, stop before 10.' },
        { q: '`break` inside a loop…', opts: ['skips to the next iteration', 'leaves the loop entirely', 'ends the program', 'restarts the loop'], a: 1, why: 'continue skips one iteration; break exits the loop.' },
        { q: 'Which of these values counts as False in an if?', opts: ['"0"', '[1]', '[]', '"False"'], a: 2, why: 'Empty containers, empty strings, 0 and None are falsy. "0" and "False" are non-empty strings — truthy.' },
        { q: 'What stops a `while` loop from running forever?', opts: ['Python stops it after 1000 rounds', 'Something in the body must eventually make the condition False (or break)', 'while loops always end on their own', 'Nothing can'], a: 1, why: 'Nothing happens automatically — the body has to change the state the condition checks, or break out.' },
        { q: 'In an if / elif / else chain, how many branches run?', opts: ['Every branch whose condition is True', 'Exactly one: the first True condition, or else', 'Always the last one', 'At most the first two'], a: 1, why: 'Python takes the first branch that matches and skips the rest.' },
      ] },
    ] },
    { title: 'Functions and collections', desc: 'Name your work; organise your data.', lessons: [
      { id: 'py-3-1', type: 'read', title: 'Functions: name your work', min: 9, md: 'py-3-1' },
      { id: 'py-3-2', type: 'read', title: 'Lists, dictionaries and friends', min: 11, md: 'py-3-2' },
      { id: 'py-3-3', type: 'code', title: 'Word counter', min: 12, lang: 'python', md: 'py-3-3.md',
        files: [{ name: 'main.py', key: 'py-3-3.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-3-3.solution.main.py' }],
        hints: [
          'text.split() breaks on any whitespace.',
          'For each word: word = raw.lower().strip(".,!?;:").',
          'The counting pattern: counts[word] = counts.get(word, 0) + 1.',
        ],
        tests: [
          { name: 'Counts case-insensitively', code: `
            assert word_count("Go go GO!") == {"go": 3}, f'Got {word_count("Go go GO!")!r}'` },
          { name: 'Strips end punctuation', code: `
            assert word_count("end. end, end!") == {"end": 3}, f'Got {word_count("end. end, end!")!r}'` },
          { name: 'A full sentence', code: `
            _r = word_count("The quick brown fox. The lazy dog! the end.")
            assert _r.get("the") == 3 and _r.get("fox") == 1 and _r.get("end") == 1, f"Got {_r!r}"` },
          { name: 'Empty string gives {}', code: `
            assert word_count("") == {}, "Empty text should give an empty dict"` },
        ] },
      { id: 'py-3-4', type: 'code', title: 'Leaderboard', min: 14, lang: 'python', md: 'py-3-4.md',
        files: [{ name: 'main.py', key: 'py-3-4.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-3-4.solution.main.py' }],
        hints: [
          'scores.items() gives (name, score) pairs.',
          'sorted(pairs, key=lambda p: (-p[1], p[0])) — negative score sorts high-to-low, name breaks ties.',
          'Slice with [:n]; slicing past the end is safe.',
        ],
        tests: [
          { name: 'Top n, highest first', code: `
            _s = {"ada": 90, "linus": 75, "grace": 90, "ken": 60}
            assert top_players(_s, 2) == [("ada", 90), ("grace", 90)], f"Got {top_players(_s, 2)!r}"` },
          { name: 'Ties break alphabetically', code: `
            _r = top_players({"zoe": 50, "amy": 50, "bo": 70}, 3)
            assert _r == [("bo", 70), ("amy", 50), ("zoe", 50)], f"Got {_r!r} — equal scores should be ordered by name"` },
          { name: 'n larger than the roster', code: `
            assert top_players({"ada": 1}, 5) == [("ada", 1)], "Asking for more players than exist should return everyone"` },
          { name: 'Average, rounded to 1 decimal', code: `
            _a = average_score({"ada": 90, "linus": 75, "grace": 90, "ken": 60})
            assert _a == 78.8, f"Got {_a!r}, expected 78.8"` },
          { name: 'Empty average is 0.0', code: `
            assert average_score({}) == 0.0, "An empty dict should give 0.0, not a crash"` },
        ] },
      { id: 'py-3-5', type: 'quiz', title: 'Check: functions and collections', min: 6, questions: [
        { q: 'A function without a `return` statement returns…', opts: ['0', '""', 'None', 'The last variable it used'], a: 2, why: 'No return means None — a common source of "NoneType" errors later.' },
        { q: '`[10, 20, 30, 40][1:3]` gives…', opts: ['[20, 30]', '[10, 20, 30]', '[20, 30, 40]', '[10, 20]'], a: 0, why: 'Slices include the start index and exclude the end.' },
        { q: 'The difference between `sorted(xs)` and `xs.sort()`?', opts: ['Nothing', 'sorted returns a new list; .sort() sorts in place and returns None', '.sort() is for numbers only', 'sorted also removes duplicates'], a: 1, why: 'Assigning xs = xs.sort() is the classic way to lose a list.' },
        { q: 'When `"x"` is missing, `d.get("x", 0)`…', opts: ['raises KeyError', 'returns None', 'returns 0', 'adds "x" to d'], a: 2, why: 'get returns the default instead of raising, and never modifies the dict.' },
        { q: '`[n * n for n in range(4)]` is…', opts: ['[1, 4, 9, 16]', '[0, 1, 4, 9]', '[0, 1, 4, 9, 16]', 'A syntax error'], a: 1, why: 'range(4) is 0..3, and each is squared.' },
        { q: '`"a-b-c".split("-")` gives…', opts: ['"abc"', '["a", "b", "c"]', '("a", "b", "c")', '["a-b-c"]'], a: 1, why: 'split cuts the string on the separator and returns a list.' },
        { q: 'Why prefer parameters over reaching for global variables inside a function?', opts: ['Globals are slower', 'The function becomes reusable and testable with any input', 'Python forbids reading globals', 'Parameters use less memory'], a: 1, why: 'A function that only depends on its inputs can be called, tested and reused anywhere.' },
      ] },
    ] },
    { title: 'Errors, classes and files', desc: 'Code that survives contact with reality.', lessons: [
      { id: 'py-4-1', type: 'read', title: 'When things go wrong: exceptions', min: 9, md: 'py-4-1' },
      { id: 'py-4-2', type: 'code', title: 'A bank account that says no', min: 16, lang: 'python', md: 'py-4-2.md',
        files: [{ name: 'main.py', key: 'py-4-2.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-4-2.solution.main.py' }],
        hints: [
          'In __init__, store the inputs: self.owner = owner, self.balance = balance.',
          'Validate first, then change the balance: if amount <= 0: raise ValueError("...").',
          '__str__ returns (not prints) the string: return f"{self.owner}: {self.balance:.2f} kr".',
          'safe_withdraw wraps the call in try/except ValueError and returns True/False.',
        ],
        tests: [
          { name: 'Stores owner and balance (with default)', code: `
            _a = BankAccount("Ada", 100)
            assert _a.owner == "Ada" and _a.balance == 100, "Store owner and balance in __init__"
            assert BankAccount("Bo").balance == 0, "balance should default to 0"` },
          { name: 'Deposits add up', code: `
            _a = BankAccount("Ada", 100)
            _a.deposit(50)
            assert _a.balance == 150, f"After depositing 50 the balance is {_a.balance!r}"` },
          { name: 'Refuses bad deposits', code: `
            _a = BankAccount("Ada", 100)
            for _bad in (0, -5):
                try:
                    _a.deposit(_bad)
                    assert False, f"deposit({_bad}) should raise ValueError"
                except ValueError:
                    pass
            assert _a.balance == 100, "A refused deposit must not change the balance"` },
          { name: 'Refuses overdrafts and bad withdrawals', code: `
            _a = BankAccount("Ada", 100)
            for _bad in (500, 0, -1):
                try:
                    _a.withdraw(_bad)
                    assert False, f"withdraw({_bad}) should raise ValueError"
                except ValueError:
                    pass
            assert _a.balance == 100, "A refused withdrawal must not change the balance"` },
          { name: 'str() formats the account', code: `
            _s = str(BankAccount("Ada", 120))
            assert _s == "Ada: 120.00 kr", f"Got {_s!r}, expected: Ada: 120.00 kr"` },
          { name: 'safe_withdraw returns True/False', code: `
            _a = BankAccount("Ada", 100)
            assert safe_withdraw(_a, 40) is True and _a.balance == 60, "A valid withdrawal returns True"
            assert safe_withdraw(_a, 500) is False and _a.balance == 60, "A refused withdrawal returns False and changes nothing"` },
        ] },
      { id: 'py-4-3', type: 'read', title: 'Classes, modules and files', min: 11, md: 'py-4-3' },
      { id: 'py-4-4', type: 'code', title: 'Save and load with JSON', min: 12, lang: 'python', md: 'py-4-4.md',
        files: [{ name: 'main.py', key: 'py-4-4.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'py-4-4.solution.main.py' }],
        hints: [
          'Writing: with open(path, "w") as f: json.dump(scores, f).',
          'Reading: json.load(f) — and wrap the open in try/except FileNotFoundError.',
        ],
        tests: [
          { name: 'Round-trips a dict', code: `
            save_scores("t1.json", {"ada": 90, "linus": 75})
            assert load_scores("t1.json") == {"ada": 90, "linus": 75}, "load_scores should return exactly what save_scores wrote"` },
          { name: 'Writes real JSON', code: `
            import json as _json
            save_scores("t2.json", {"x": 1})
            with open("t2.json") as _f:
                assert _json.load(_f) == {"x": 1}, "The file should contain plain JSON"` },
          { name: 'Missing file gives {}', code: `
            assert load_scores("definitely-missing-42.json") == {}, "A missing file should give {} — catch FileNotFoundError"` },
          { name: 'Numbers stay numbers', code: `
            save_scores("t3.json", {"a": 1})
            _v = load_scores("t3.json")["a"]
            assert _v == 1 and isinstance(_v, int), "JSON keeps ints as ints — no str() conversions needed"` },
        ] },
      { id: 'py-4-5', type: 'quiz', title: 'Check: errors, classes, files', min: 5, questions: [
        { q: 'Which block runs no matter what happens?', opts: ['else', 'finally', 'except', 'with'], a: 1, why: 'finally always runs — it exists for cleanup.' },
        { q: 'Why catch `except ValueError` rather than a bare `except:`?', opts: ['Bare except is a syntax error', 'A bare except also hides bugs you did not expect', 'ValueError is faster', 'There is no difference'], a: 1, why: 'Catch what you can handle; let everything else surface so you can fix it.' },
        { q: 'Inside a method, `self` is…', opts: ['the class', 'the module', 'the object the method was called on', 'optional decoration'], a: 2, why: 'golf.drive(120) becomes Car.drive(golf, 120) — self is golf.' },
        { q: 'The advantage of `with open(...) as f:` is…', opts: ['It is shorter, that is all', 'The file is closed automatically, even if an exception happens', 'It reads faster', 'It creates missing files'], a: 1, why: 'with guarantees cleanup — the same reason finally exists.' },
        { q: '`json.dumps(data)`…', opts: ['writes data to disk', 'returns data as a JSON string', 'parses a JSON string', 'pretty-prints to the console'], a: 1, why: 'dumps = dump-to-string. json.dump (no s) writes to a file.' },
        { q: '`raise ValueError("too big")` is the right move when…', opts: ['you want to log a warning', 'a function receives input it cannot sensibly handle', 'you want to leave a loop', 'you want to print an error'], a: 1, why: 'Refusing loudly beats returning nonsense — callers can catch and decide.' },
      ] },
    ] },
    { title: 'Project', desc: 'Everything so far, in one build.', lessons: [
      { id: 'py-5-1', type: 'project', title: 'Project: inventory manager', min: 45, lang: 'python', md: 'py-5-1.md',
        files: [
          { name: 'inventory.py', key: 'py-5-1.starter.inventory.py' },
          { name: 'main.py', key: 'py-5-1.starter.main.py' },
        ], main: 'main.py',
        solution: [
          { name: 'inventory.py', key: 'py-5-1.solution.inventory.py' },
          { name: 'main.py', key: 'py-5-1.solution.main.py' },
        ],
        hints: [
          'Keep self.items as a dict keyed by name — add, remove and merge become one-liners.',
          'find: q = query.lower(), then a list comprehension with "q in item.name.lower()", then sorted(..., key=lambda i: i.name).',
          'save: build a list of plain dicts, json.dump it. load: cls() then add() each row — merging comes free.',
          'report: build a list of lines and "chr(10).join(lines)" — or just join with a newline. f"{name:<20}" pads left-aligned to 20 characters.',
        ],
        tests: [
          { name: 'Item stores its three attributes', code: `
            from inventory import Item
            _i = Item("Torch", 249.0, 4)
            assert _i.name == "Torch" and _i.price == 249.0 and _i.quantity == 4, "Item should keep name, price and quantity"` },
          { name: 'add() merges duplicates by name', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Torch", 249.0, 2))
            _inv.add(Item("Torch", 249.0, 3))
            _found = _inv.find("torch")
            assert len(_found) == 1 and _found[0].quantity == 5, "Adding the same name twice should merge quantities"` },
          { name: 'find() is case-insensitive and sorted', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Wiper blades", 120.0, 8))
            _inv.add(Item("Wheel jack", 899.0, 2))
            _inv.add(Item("Torch", 249.0, 4))
            _names = [i.name for i in _inv.find("w")]
            assert _names == ["Wheel jack", "Wiper blades"], f"find('w') gave {_names!r}"
            assert [i.name for i in _inv.find("TORCH")] == ["Torch"], "The search should ignore case"` },
          { name: 'remove() reduces, drops at zero', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Torch", 249.0, 4))
            _inv.remove("Torch", 3)
            assert _inv.find("Torch")[0].quantity == 1, "remove should subtract the quantity"
            _inv.remove("Torch", 1)
            assert _inv.find("Torch") == [], "Quantity 0 should remove the item entirely"` },
          { name: 'remove() raises the right errors', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Torch", 249.0, 2))
            try:
                _inv.remove("Ghost", 1)
                assert False, "Unknown name should raise KeyError"
            except KeyError:
                pass
            try:
                _inv.remove("Torch", 5)
                assert False, "Removing more than the stock should raise ValueError"
            except ValueError:
                pass
            assert _inv.find("Torch")[0].quantity == 2, "A refused remove must change nothing"` },
          { name: 'total_value() and low_stock()', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Wiper blades", 120.0, 8))
            _inv.add(Item("Jack", 899.0, 2))
            _inv.add(Item("Torch", 249.0, 4))
            assert abs(_inv.total_value() - 3754.0) < 1e-6, f"total_value gave {_inv.total_value()!r}, expected 3754.0"
            assert [i.name for i in _inv.low_stock()] == ["Jack", "Torch"], "Default threshold 5, sorted by name"
            assert [i.name for i in _inv.low_stock(3)] == ["Jack"], "The threshold parameter should be respected"` },
          { name: 'save() / Inventory.load() round-trip', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Torch", 249.0, 4))
            _inv.add(Item("Jack", 899.0, 2))
            _inv.save("inv-test.json")
            _loaded = Inventory.load("inv-test.json")
            assert abs(_loaded.total_value() - _inv.total_value()) < 1e-6, "The loaded inventory should match what was saved"
            assert [i.name for i in _loaded.find("")] == ["Jack", "Torch"], "load is a classmethod returning a new Inventory"` },
          { name: 'report() lists items and the total', code: `
            from inventory import Inventory, Item
            _inv = Inventory()
            _inv.add(Item("Torch", 249.0, 4))
            _inv.add(Item("Jack", 899.0, 2))
            _rep = _inv.report()
            assert isinstance(_rep, str) and "Torch" in _rep and "Jack" in _rep and "Total" in _rep, "report() returns a string with every item and a Total line"
            assert _rep.index("Jack") < _rep.index("Torch"), "Items should appear sorted by name"` },
        ] },
    ] },
  ],
},
{
  id: 'web', name: 'Web Development', icon: '🌐', tint: '#FFE9DC', fg: '#C9530E',
  tagline: 'HTML, CSS and JavaScript — pages that respond to people.',
  outcomes: [
    'Structure pages with semantic HTML',
    'Style and lay out with flexbox and grid',
    'Make pages responsive to any screen',
    'Drive the DOM with JavaScript events',
    'Load data asynchronously with fetch',
    'Ship a complete multi-file app',
  ],
  modules: [
    { title: 'HTML', desc: 'The structure of every page.', lessons: [
      { id: 'web-1-1', type: 'read', title: 'How a web page is built', min: 9, md: 'web-1-1' },
      { id: 'web-1-2', type: 'code', title: 'Profile card page', min: 14, lang: 'web', md: 'web-1-2.md',
        files: [{ name: 'index.html', key: 'web-1-2.starter.index.html' }], main: 'index.html',
        solution: [{ name: 'index.html', key: 'web-1-2.solution.index.html' }],
        hints: [
          'Skeleton first: <header> with the <h1>, then <main> with everything else.',
          'A list is <ul> around three or more <li> items.',
          'The link needs both an href="https://..." and text between the tags.',
        ],
        tests: [
          { name: 'A header with the name', code: `
            const h1 = document.querySelector("header h1");
            assert(h1, "Needs an <h1> inside a <header>");
            assert(h1.textContent.trim().length > 0, "Put the name inside the <h1>");` },
          { name: 'Content lives in <main>', code: `
            assert(document.querySelector("main"), "Wrap the content in a <main> element");` },
          { name: 'Image with alt text', code: `
            const img = document.querySelector("img");
            assert(img, "Needs an <img>");
            assert((img.getAttribute("alt") || "").trim().length > 0, "The alt attribute must describe the image");` },
          { name: 'A bio paragraph', code: `
            assert(document.querySelector("main p"), "Add a <p> with a short bio inside <main>");` },
          { name: 'At least three skills in a list', code: `
            const items = document.querySelectorAll("ul li");
            assert(items.length >= 3, "Found " + items.length + " <li> — need at least 3 inside a <ul>");` },
          { name: 'A real link', code: `
            const a = document.querySelector("a[href]");
            assert(a, "Needs an <a> with an href");
            assert(a.getAttribute("href").indexOf("https://") === 0, "The href should start with https://");
            assert(a.textContent.trim().length > 0, "Give the link visible text");` },
        ] },
      { id: 'web-1-3', type: 'quiz', title: 'Check: HTML', min: 5, questions: [
        { q: 'What does the `alt` attribute on `<img>` do?', opts: ['Sets the hover tooltip', 'Describes the image for screen readers and when it fails to load', 'Renames the file', 'Makes it load faster'], a: 1, why: 'alt is the image in words — accessibility and resilience in one attribute.' },
        { q: 'Which is correctly structured?', opts: ['<ul><li>One</li></ul>', '<li><ul>One</ul></li>', '<ul>One</ul>', '<list><item>One</item></list>'], a: 0, why: 'Items live inside the list; the text lives inside the items.' },
        { q: 'In `<a href="…">`, what is href?', opts: ['An attribute saying where the link goes', 'A tag', 'A CSS property', 'The visible label'], a: 0, why: 'Attributes are extra information on the opening tag.' },
        { q: 'Why use `<main>`, `<nav>`, `<footer>` instead of `<div>` everywhere?', opts: ['They load faster', 'They describe the structure to browsers, screen readers and search engines', 'div is deprecated', 'They come pre-styled'], a: 1, why: 'Semantics are for machines and future readers — the pixels look the same.' },
        { q: 'How many `<h1>` elements should a page normally have?', opts: ['As many as you like — it is just styling', 'One: the page title; sections use h2 and below', 'Zero, h1 is deprecated', 'Exactly six'], a: 1, why: 'Headings form the page outline; one h1 keeps it coherent.' },
        { q: 'Which element collects a line of typed text?', opts: ['<button>', '<span>', '<input>', '<text>'], a: 2, why: '<input> (with a <label>) is the form control for text.' },
      ] },
    ] },
    { title: 'CSS', desc: 'Looks, layout, responsiveness.', lessons: [
      { id: 'web-2-1', type: 'read', title: 'Selectors, the box model, and layout', min: 12, md: 'web-2-1' },
      { id: 'web-2-2', type: 'code', title: 'Style the card', min: 14, lang: 'web', md: 'web-2-2.md',
        files: [
          { name: 'index.html', key: 'web-2-2.starter.index.html', ro: true },
          { name: 'style.css', key: 'web-2-2.starter.style.css' },
        ], main: 'index.html',
        solution: [{ name: 'style.css', key: 'web-2-2.solution.style.css' }],
        hints: [
          'One rule per requirement: .card { border-radius: 16px; padding: 24px; background: #fff; box-shadow: 0 10px 30px rgba(0,0,0,.08); }.',
          'The skills list keeps its bullets unless you remove them: list-style: none; padding: 0; — then display: flex; gap: 8px.',
        ],
        tests: [
          { name: 'The card has shape', code: `
            const card = document.querySelector(".card");
            assert(card, "Where did .card go?");
            const cs = getComputedStyle(card);
            assert(parseFloat(cs.borderTopLeftRadius) > 0, "Give .card a border-radius");
            assert(parseFloat(cs.paddingTop) >= 12, ".card needs at least 12px of padding");` },
          { name: 'The card lifts off the page', code: `
            const cs = getComputedStyle(document.querySelector(".card"));
            assert(cs.boxShadow && cs.boxShadow !== "none", "Add a box-shadow to .card");
            const bg = cs.backgroundColor;
            assert(bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent", "Give .card a background colour");` },
          { name: 'Skills flow as a flex row', code: `
            const s = getComputedStyle(document.querySelector(".skills"));
            assert(s.display === "flex", ".skills should be display: flex (got " + s.display + ")");
            assert(parseFloat(s.columnGap) > 0, "Add a gap between the tags");` },
          { name: 'Tags look like tags', code: `
            const t = getComputedStyle(document.querySelector(".tag"));
            assert(parseFloat(t.paddingLeft) > 0, "Each .tag needs some padding");
            assert(parseFloat(t.borderTopLeftRadius) > 0, "Round the .tag corners");` },
          { name: 'The heading has a colour', code: `
            const c = getComputedStyle(document.querySelector("h1")).color;
            assert(c !== "rgb(0, 0, 0)", "Change the h1 colour away from default black");` },
        ] },
      { id: 'web-2-3', type: 'code', title: 'Navbar and responsive gallery', min: 16, lang: 'web', md: 'web-2-3.md',
        files: [
          { name: 'index.html', key: 'web-2-3.starter.index.html', ro: true },
          { name: 'style.css', key: 'web-2-3.starter.style.css' },
        ], main: 'index.html',
        solution: [{ name: 'style.css', key: 'web-2-3.solution.style.css' }],
        hints: [
          'nav { display: flex; justify-content: space-between; align-items: center; }.',
          '.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; } and .gallery img { width: 100%; }.',
          'The media query wraps a normal rule: @media (max-width: 600px) { .gallery { grid-template-columns: 1fr; } }.',
        ],
        tests: [
          { name: 'Nav is a flex row, spread out', code: `
            const n = getComputedStyle(document.querySelector("nav"));
            assert(n.display === "flex", "nav should be display: flex (got " + n.display + ")");
            assert(n.justifyContent === "space-between", "Use justify-content: space-between (got " + n.justifyContent + ")");
            assert(n.alignItems === "center", "Use align-items: center (got " + n.alignItems + ")");` },
          { name: 'The gallery is a grid with a gap', code: `
            const g = getComputedStyle(document.querySelector(".gallery"));
            assert(g.display === "grid", ".gallery should be display: grid (got " + g.display + ")");
            assert(parseFloat(g.columnGap) > 0 || parseFloat(g.rowGap) > 0, "Add a gap to the grid");` },
          { name: 'Three columns wide, one narrow', code: `
            const cols = getComputedStyle(document.querySelector(".gallery")).gridTemplateColumns.split(" ").filter(function (x) { return x.length > 0; }).length;
            if (window.innerWidth > 600) {
              assert(cols === 3, "Expected 3 columns at " + window.innerWidth + "px, found " + cols);
            } else {
              assert(cols === 1, "Expected 1 column at " + window.innerWidth + "px (your preview is narrow), found " + cols);
            }` },
          { name: 'Images fill their cell', code: `
            const gallery = document.querySelector(".gallery");
            const img = gallery.querySelector("img");
            const cs = getComputedStyle(gallery);
            const cols = cs.gridTemplateColumns.split(" ").filter(function (x) { return x.length > 0; }).length;
            const gap = parseFloat(cs.columnGap) || 0;
            const expected = (gallery.getBoundingClientRect().width - gap * (cols - 1)) / cols;
            const actual = img.getBoundingClientRect().width;
            assert(Math.abs(actual - expected) < 8, "Images should fill their grid cell — set .gallery img { width: 100%; } (cell ~" + Math.round(expected) + "px, image " + Math.round(actual) + "px)");` },
          { name: 'A media query handles small screens', code: `
            const cssText = Array.prototype.map.call(document.querySelectorAll("style"), function (s) { return s.textContent; }).join(" ");
            assert(/@media[^{]*max-width\\s*:\\s*600px/.test(cssText), "Add @media (max-width: 600px) { ... }");
            assert(/@media[^{]*600px[^{]*\\{[\\s\\S]*?\\.gallery[\\s\\S]*?grid-template-columns\\s*:\\s*1fr/.test(cssText), "Inside the media query, set .gallery to a single column (grid-template-columns: 1fr)");` },
        ] },
      { id: 'web-2-4', type: 'quiz', title: 'Check: CSS', min: 5, questions: [
        { q: 'Which selector targets elements with `class="card"`?', opts: ['.card', '#card', 'card', '*card'], a: 0, why: 'Dot for classes, hash for ids, bare names for element types.' },
        { q: 'In the box model, padding is…', opts: ['space outside the border', 'space between the content and the border', 'the border itself', 'the same as margin'], a: 1, why: 'Content → padding → border → margin, inside out.' },
        { q: 'Two rules colour the same element differently. Which wins?', opts: ['The first one written', 'The more specific selector; among equals, the later one', 'Random', 'The shorter one'], a: 1, why: 'Specificity first (#id > .class > element), source order as the tiebreak.' },
        { q: '`display: flex` on a container…', opts: ['hides it', 'lays out its children along a row or column with easy alignment', 'makes text bold', 'only works on divs'], a: 1, why: 'Flexbox is the go-to for one-dimensional layout.' },
        { q: '`@media (max-width: 600px) { … }` means…', opts: ['only screens wider than 600px', 'the rules inside apply when the viewport is 600px or narrower', 'set the page width to 600px', 'load a smaller image'], a: 1, why: 'Media queries switch rule sets by viewport conditions.' },
        { q: 'Which unit scales with the user’s base font size?', opts: ['px', 'rem', 'cm', 'vh'], a: 1, why: '1rem = the root font size, so text set in rem respects user preferences.' },
      ] },
    ] },
    { title: 'JavaScript', desc: 'Logic, the DOM, and async.', lessons: [
      { id: 'web-3-1', type: 'read', title: 'JavaScript essentials', min: 12, md: 'web-3-1' },
      { id: 'web-3-2', type: 'code', title: 'Shopping cart logic', min: 14, lang: 'js', md: 'web-3-2.md',
        files: [{ name: 'cart.js', key: 'web-3-2.starter.cart.js' }], main: 'cart.js',
        solution: [{ name: 'cart.js', key: 'web-3-2.solution.cart.js' }],
        hints: [
          'cartTotal: items.reduce((sum, item) => sum + item.price * item.qty, 0).',
          'formatPrice: "$" + amount.toFixed(2) — toFixed returns a string with exactly 2 decimals.',
          'applyDiscount: normalise with (code || "").toUpperCase() so undefined and "half" both behave.',
          'inStock: filter first, then map to names.',
        ],
        tests: [
          { name: 'cartTotal sums price × qty', code: `
            assertEqual(cartTotal([{ name: "a", price: 120, qty: 2 }, { name: "b", price: 10, qty: 3 }]), 270);
            assertEqual(cartTotal([]), 0, "An empty cart totals 0");` },
          { name: 'formatPrice pads to two decimals', code: `
            assertEqual(formatPrice(12.5), "$12.50");
            assertEqual(formatPrice(1283), "$1283.00");
            assertEqual(formatPrice(0.1), "$0.10");` },
          { name: 'applyDiscount knows its codes', code: `
            assertEqual(applyDiscount(100, "SAVE10"), 90);
            assertEqual(applyDiscount(100, "half"), 50, "Codes are case-insensitive");
            assertEqual(applyDiscount(100, "NOPE"), 100, "Unknown codes change nothing");
            assertEqual(applyDiscount(100, undefined), 100, "No code changes nothing");` },
          { name: 'inStock filters and maps', code: `
            assertEqual(inStock([{ name: "a", price: 1, qty: 0 }, { name: "b", price: 1, qty: 2 }, { name: "c", price: 1, qty: 1 }]), ["b", "c"]);
            assertEqual(inStock([]), []);` },
        ] },
      { id: 'web-3-3', type: 'read', title: 'The DOM and events', min: 11, md: 'web-3-3' },
      { id: 'web-3-4', type: 'code', title: 'Counter', min: 12, lang: 'web', md: 'web-3-4.md',
        files: [
          { name: 'index.html', key: 'web-3-4.starter.index.html', ro: true },
          { name: 'app.js', key: 'web-3-4.starter.app.js' },
        ], main: 'index.html',
        solution: [{ name: 'app.js', key: 'web-3-4.solution.app.js' }],
        hints: [
          'render() is one line: countEl.textContent = count.',
          'Each button: document.querySelector("#increment").addEventListener("click", () => { count += 1; render(); }).',
          'Guard the decrement: if (count > 0) count -= 1.',
        ],
        tests: [
          { name: 'Starts at 0', code: `
            assert(document.querySelector("#count").textContent.trim() === "0", "The count should show 0 at the start");` },
          { name: '+ increments', code: `
            const c = document.querySelector("#count");
            document.querySelector("#increment").click();
            document.querySelector("#increment").click();
            assert(c.textContent.trim() === "2", "After two + clicks the count shows " + c.textContent.trim() + " instead of 2");` },
          { name: '− decrements, never below 0', code: `
            const c = document.querySelector("#count");
            document.querySelector("#decrement").click();
            assert(c.textContent.trim() === "1", "Expected 1 after one −, got " + c.textContent.trim());
            for (let i = 0; i < 5; i++) document.querySelector("#decrement").click();
            assert(c.textContent.trim() === "0", "The count must not go below 0 (got " + c.textContent.trim() + ")");` },
          { name: 'Reset returns to 0', code: `
            document.querySelector("#increment").click();
            document.querySelector("#increment").click();
            document.querySelector("#reset").click();
            assert(document.querySelector("#count").textContent.trim() === "0", "Reset should put the count back to 0");` },
        ] },
      { id: 'web-3-5', type: 'code', title: 'To-do list', min: 18, lang: 'web', md: 'web-3-5.md',
        files: [
          { name: 'index.html', key: 'web-3-5.starter.index.html', ro: true },
          { name: 'app.js', key: 'web-3-5.starter.app.js' },
        ], main: 'index.html',
        solution: [{ name: 'app.js', key: 'web-3-5.solution.app.js' }],
        hints: [
          'In the submit handler: event.preventDefault(), then input.value.trim() — return early if empty.',
          'render(): clear the list, create an <li> per task, set dataset.index, toggle the done class.',
          'One click listener on the list; event.target.closest("li") tells you which item.',
        ],
        tests: [
          { name: 'Adding a task creates a list item', code: `
            const input = document.querySelector("#new-task");
            const form = document.querySelector("#task-form");
            input.value = "Order oil filters";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            const items = document.querySelectorAll("#tasks li");
            assert(items.length === 1, "Expected 1 task after adding, found " + items.length);
            assert(items[0].textContent.indexOf("Order oil filters") !== -1, "The task text should appear in the item");
            assert(input.value === "", "Clear the input after adding");` },
          { name: 'Blank input is ignored', code: `
            const input = document.querySelector("#new-task");
            const form = document.querySelector("#task-form");
            input.value = "   ";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            assert(document.querySelectorAll("#tasks li").length === 1, "Whitespace-only input should not add a task");` },
          { name: 'Clicking toggles done', code: `
            let li = document.querySelector("#tasks li");
            li.click();
            li = document.querySelector("#tasks li");
            assert(li.classList.contains("done"), "Clicking an item should toggle the class done on");
            li.click();
            li = document.querySelector("#tasks li");
            assert(!li.classList.contains("done"), "Clicking again should toggle it off");` },
          { name: 'Remaining counts undone tasks', code: `
            const input = document.querySelector("#new-task");
            const form = document.querySelector("#task-form");
            input.value = "Check tyre stock";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            input.value = "Sweep bay 2";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            assert(document.querySelector("#remaining").textContent.trim() === "3", "With 3 open tasks, #remaining should show 3 (got " + document.querySelector("#remaining").textContent.trim() + ")");
            document.querySelectorAll("#tasks li")[1].click();
            assert(document.querySelector("#remaining").textContent.trim() === "2", "#remaining should update when a task is marked done");` },
        ] },
      { id: 'web-3-6', type: 'read', title: 'Async: promises, fetch and APIs', min: 11, md: 'web-3-6' },
      { id: 'web-3-7', type: 'code', title: 'Load and render data', min: 18, lang: 'web', md: 'web-3-7.md',
        files: [
          { name: 'index.html', key: 'web-3-7.starter.index.html', ro: true },
          { name: 'app.js', key: 'web-3-7.starter.app.js' },
        ], main: 'index.html',
        solution: [{ name: 'app.js', key: 'web-3-7.solution.app.js' }],
        hints: [
          'loadUsers: const response = await fakeFetch("/api/users"); if (!response.ok) throw new Error(...); return await response.json().',
          'The click handler is async too: set the status, try { await } catch { … }.',
          'Template for the status: "Loaded " + users.length + " users".',
        ],
        tests: [
          { name: 'loadUsers is async and returns the array', code: `
            assert(typeof loadUsers === "function", "Define a function called loadUsers");
            const p = loadUsers();
            assert(p && typeof p.then === "function", "loadUsers should be async (return a promise)");
            const users = await p;
            assert(Array.isArray(users) && users.length === 3 && users[0].name === "Ada Lovelace", "loadUsers should resolve with the 3 users from /api/users");` },
          { name: 'Clicking Load renders the names', code: `
            document.querySelector("#users").innerHTML = "";
            document.querySelector("#load").click();
            await new Promise(function (r) { setTimeout(r, 450); });
            const items = document.querySelectorAll("#users li");
            assert(items.length === 3, "Expected 3 list items after loading, found " + items.length);
            assert(items[1].textContent.indexOf("Grace Hopper") !== -1, "Each item should show the user name");` },
          { name: 'The status tells the story', code: `
            document.querySelector("#load").click();
            const st = document.querySelector("#status");
            await new Promise(function (r) { setTimeout(r, 30); });
            assert(st.textContent.indexOf("Loading") === 0, "Show Loading… immediately (got: " + st.textContent + ")");
            await new Promise(function (r) { setTimeout(r, 450); });
            assert(st.textContent === "Loaded 3 users", "Expected: Loaded 3 users — got: " + st.textContent);` },
          { name: 'The failure path is handled', code: `
            const orig = window.fakeFetch;
            window.fakeFetch = function () { return orig("/api/missing"); };
            document.querySelector("#load").click();
            await new Promise(function (r) { setTimeout(r, 450); });
            window.fakeFetch = orig;
            assert(document.querySelector("#status").textContent === "Could not load users", "On failure #status should say: Could not load users (got: " + document.querySelector("#status").textContent + ")");
            assert(document.querySelectorAll("#users li").length === 0, "The list should be empty after a failure");` },
        ] },
      { id: 'web-3-8', type: 'quiz', title: 'Check: JavaScript', min: 6, questions: [
        { q: '`const` vs `let`?', opts: ['const is faster', 'const cannot be reassigned; let can', 'let is global', 'No difference'], a: 1, why: 'Default to const; reach for let only when a value genuinely changes.' },
        { q: 'Why `===` instead of `==`?', opts: ['=== also compares types instead of silently converting them', '== is deprecated', '=== is required by strict mode', 'They are identical'], a: 0, why: '"5" == 5 is true; "5" === 5 is false. Strict equality avoids surprises.' },
        { q: '`[1, 2, 3].map(n => n * 2)` gives…', opts: ['[2, 4, 6]', '6', '[1, 2, 3, 2, 4, 6]', 'undefined'], a: 0, why: 'map builds a new array with each element transformed.' },
        { q: '`document.querySelector(".item")` returns…', opts: ['all matching elements', 'the first matching element, or null', 'a string of HTML', 'true or false'], a: 1, why: 'querySelectorAll returns all matches; querySelector just the first.' },
        { q: '`event.preventDefault()` in a submit handler…', opts: ['stops the page from reloading so your code can handle the form', 'deletes the form', 'submits it twice', 'clears the inputs'], a: 0, why: 'The default action of submit is a full page navigation — you almost always cancel it.' },
        { q: 'Why `textContent` instead of `innerHTML` for user input?', opts: ['textContent is shorter', 'innerHTML parses the text as HTML — user input could inject markup or scripts', 'textContent is faster, that is all', 'innerHTML only works on divs'], a: 1, why: 'That injection is called XSS. Text goes in as text.' },
        { q: '`await` can be used…', opts: ['anywhere', 'inside functions marked async', 'only in loops', 'only with fetch'], a: 1, why: 'await pauses the async function it lives in — so the function must be async.' },
      ] },
    ] },
    { title: 'Project', desc: 'A complete interactive app.', lessons: [
      { id: 'web-4-1', type: 'project', title: 'Project: task board', min: 50, lang: 'web', md: 'web-4-1.md',
        files: [
          { name: 'index.html', key: 'web-4-1.starter.index.html' },
          { name: 'style.css', key: 'web-4-1.starter.style.css' },
          { name: 'app.js', key: 'web-4-1.starter.app.js' },
        ], main: 'index.html',
        solution: [
          { name: 'index.html', key: 'web-4-1.solution.index.html' },
          { name: 'style.css', key: 'web-4-1.solution.style.css' },
          { name: 'app.js', key: 'web-4-1.solution.app.js' },
        ],
        hints: [
          'Write the three <section class="column"> blocks by hand in index.html — only the cards are dynamic.',
          'render(): for each status, find its column, rebuild ul.cards from the filtered array, set the .count text.',
          'Give each card li dataset.id = card.id; one click listener on .board handles both buttons via event.target.closest(".move" / ".delete").',
          'Only append the .move button when status !== "done".',
        ],
        tests: [
          { name: 'Three columns, right structure', code: `
            const cols = document.querySelectorAll(".board .column");
            assert(cols.length === 3, "Found " + cols.length + " .column elements — need 3 inside .board");
            const statuses = Array.prototype.map.call(cols, function (c) { return c.dataset.status; });
            ["todo", "doing", "done"].forEach(function (s) {
              assert(statuses.indexOf(s) !== -1, "Missing a column with data-status=" + s);
            });
            Array.prototype.forEach.call(cols, function (c) {
              assert(c.querySelector("h2 .count"), "Each column h2 needs a .count span");
              assert(c.querySelector("ul.cards"), "Each column needs a <ul class=cards>");
            });` },
          { name: 'The board is laid out', code: `
            const d = getComputedStyle(document.querySelector(".board")).display;
            assert(d === "grid" || d === "flex", ".board should use grid or flex (got " + d + ")");` },
          { name: 'Adding a card puts it in To do', code: `
            const input = document.querySelector("#card-title");
            const form = document.querySelector("#new-card");
            input.value = "Price the winter tyres";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            const cards = document.querySelectorAll(".column[data-status=todo] .card");
            assert(cards.length === 1, "Expected the new card in the todo column, found " + cards.length);
            assert(cards[0].textContent.indexOf("Price the winter tyres") !== -1, "The card should show its title");
            assert(input.value === "", "Clear the input after adding");
            input.value = "   ";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            assert(document.querySelectorAll(".card").length === 1, "Empty titles should be ignored");` },
          { name: 'Counts stay correct', code: `
            const input = document.querySelector("#card-title");
            const form = document.querySelector("#new-card");
            input.value = "Sweep bay 2";
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            const todo = document.querySelector(".column[data-status=todo]");
            assert(todo.querySelector(".count").textContent.trim() === "2", "The todo count should show 2 (got " + todo.querySelector(".count").textContent.trim() + ")");` },
          { name: 'Move walks the pipeline', code: `
            const first = document.querySelector(".column[data-status=todo] .card .move");
            assert(first, "Cards outside done need a .move button");
            first.click();
            assert(document.querySelectorAll(".column[data-status=doing] .card").length === 1, "The card should move to doing");
            const again = document.querySelector(".column[data-status=doing] .card .move");
            assert(again, "Cards in doing also need a .move button");
            again.click();
            const doneCards = document.querySelectorAll(".column[data-status=done] .card");
            assert(doneCards.length === 1, "The card should end up in done");
            assert(!doneCards[0].querySelector(".move"), "Cards in done should not have a .move button");` },
          { name: 'Delete removes a card', code: `
            const before = document.querySelectorAll(".card").length;
            const del = document.querySelector(".card .delete");
            assert(del, "Every card needs a .delete button");
            del.click();
            assert(document.querySelectorAll(".card").length === before - 1, "Deleting should remove the card");` },
          { name: 'Every count matches its column', code: `
            Array.prototype.forEach.call(document.querySelectorAll(".column"), function (col) {
              const n = col.querySelectorAll(".card").length;
              const shown = col.querySelector(".count").textContent.trim();
              assert(String(n) === shown, "Column " + col.dataset.status + " shows " + shown + " but holds " + n + " card(s)");
            });` },
        ] },
    ] },
  ],
},
{
  id: 'backend', name: 'Backend Development', icon: '🖥️', tint: '#E1F4E8', fg: '#177A45',
  tagline: 'Servers, APIs, databases and security — after the request leaves the browser.',
  outcomes: [
    'Speak HTTP: methods, status codes, REST',
    'Design and implement a JSON API',
    'Query and update SQLite with SQL',
    'Store passwords safely with salted hashes',
    'Shut the door on SQL injection',
    'Know your way to Flask, FastAPI and Express',
  ],
  modules: [
    { title: 'HTTP and APIs', desc: 'The request/response contract.', lessons: [
      { id: 'be-1-1', type: 'read', title: 'How the web talks: HTTP', min: 12, md: 'be-1-1' },
      { id: 'be-1-2', type: 'quiz', title: 'Check: HTTP & REST', min: 6, questions: [
        { q: 'A successful `POST` that created something should return…', opts: ['200', '201', '204', '301'], a: 1, why: '201 Created — with the new resource in the body.' },
        { q: '`404` means…', opts: ['the server crashed', 'the resource does not exist', 'you are not allowed to see it', 'the JSON was malformed'], a: 1, why: 'Wrong path or wrong id: nothing there.' },
        { q: 'Status codes starting with 4 mean…', opts: ['success', 'the client’s request was wrong', 'the server failed', 'redirects'], a: 1, why: '4xx: fix the request. 5xx: fix the server.' },
        { q: 'Which follows REST conventions for deleting book 42?', opts: ['POST /deleteBook?id=42', 'GET /books/delete/42', 'DELETE /books/42', 'REMOVE /book42'], a: 2, why: 'Nouns in the path, the verb in the method.' },
        { q: 'HTTP being stateless means…', opts: ['it cannot use HTTPS', 'the server keeps no memory between requests — state lives in databases, sessions or tokens', 'only GET is allowed', 'responses cannot contain JSON'], a: 1, why: 'Every request must carry or reference whatever context it needs.' },
        { q: '`401` vs `403`?', opts: ['They are the same', '401: not (correctly) authenticated. 403: authenticated, but not allowed', '401 is only for admins', '403 means try again later'], a: 1, why: '401 asks "who are you?"; 403 says "I know, and no".' },
        { q: 'Query parameters like `?author=le+guin` are best for…', opts: ['identifying one resource', 'filtering or sorting a collection', 'authentication', 'request bodies'], a: 1, why: 'Path identifies, query refines.' },
      ] },
      { id: 'be-1-3', type: 'code', title: 'Build a REST handler', min: 25, lang: 'python', md: 'be-1-3.md',
        files: [{ name: 'main.py', key: 'be-1-3.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'be-1-3.solution.main.py' }],
        hints: [
          'parts = [p for p in path.split("/") if p] gives ["todos"] or ["todos", "3"].',
          'Write a find_todo(todo_id) helper — three routes need it.',
          'Handle the collection (parts == ["todos"]) and the item (len(parts) == 2) as two blocks; fall through to 404.',
          'The id in the path is a string: int(parts[1]), guarded by parts[1].isdigit().',
        ],
        tests: [
          { name: 'POST creates a todo (201)', code: `
            TODOS.clear()
            _status, _todo = handle_request("POST", "/todos", {"title": "Order brake pads"})
            assert _status == 201, f"Expected 201, got {_status}"
            assert _todo["title"] == "Order brake pads" and _todo["done"] is False and "id" in _todo, f"Got {_todo!r}"` },
          { name: 'GET /todos lists them in order', code: `
            TODOS.clear()
            handle_request("POST", "/todos", {"title": "a"})
            handle_request("POST", "/todos", {"title": "b"})
            _status, _list = handle_request("GET", "/todos")
            assert _status == 200 and [t["title"] for t in _list] == ["a", "b"], f"Got {(_status, _list)!r}"` },
          { name: 'POST without a title → 400', code: `
            TODOS.clear()
            _status, _err = handle_request("POST", "/todos", {})
            assert _status == 400 and "error" in _err, f"Got {(_status, _err)!r}"
            assert handle_request("POST", "/todos", {"title": ""})[0] == 400, "An empty title should also be rejected"` },
          { name: 'GET /todos/<id> finds one — or 404s', code: `
            TODOS.clear()
            _todo = handle_request("POST", "/todos", {"title": "find me"})[1]
            _status, _found = handle_request("GET", "/todos/" + str(_todo["id"]))
            assert _status == 200 and _found["title"] == "find me", f"Got {(_status, _found)!r}"
            assert handle_request("GET", "/todos/999999")[0] == 404, "An unknown id should give 404"` },
          { name: 'PATCH updates done', code: `
            TODOS.clear()
            _todo = handle_request("POST", "/todos", {"title": "x"})[1]
            _status, _updated = handle_request("PATCH", "/todos/" + str(_todo["id"]), {"done": True})
            assert _status == 200 and _updated["done"] is True, f"Got {(_status, _updated)!r}"` },
          { name: 'DELETE removes (204), then 404', code: `
            TODOS.clear()
            _todo = handle_request("POST", "/todos", {"title": "x"})[1]
            _id = str(_todo["id"])
            assert handle_request("DELETE", "/todos/" + _id) == (204, None), "DELETE should answer (204, None)"
            assert handle_request("GET", "/todos/" + _id)[0] == 404, "The deleted todo should be gone"` },
          { name: 'Unknown path 404, wrong method 405', code: `
            assert handle_request("GET", "/nope")[0] == 404, "Unknown paths give 404"
            assert handle_request("DELETE", "/todos")[0] == 405, "DELETE on the collection gives 405"` },
        ] },
    ] },
    { title: 'Databases', desc: 'SQL and SQLite from Python.', lessons: [
      { id: 'be-2-1', type: 'read', title: 'Databases and SQL', min: 13, md: 'be-2-1' },
      { id: 'be-2-2', type: 'code', title: 'Query the shop database', min: 22, lang: 'python', md: 'be-2-2.md', packages: ['sqlite3'],
        files: [{ name: 'main.py', key: 'be-2-2.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'be-2-2.solution.main.py' }],
        hints: [
          'total_revenue: SELECT SUM(amount) FROM orders — fetchone() gives a 1-tuple.',
          'Both grouped queries share a shape: SELECT c.city, SUM(o.amount) AS total FROM customers c JOIN orders o ON o.customer_id = c.id GROUP BY … ORDER BY total DESC.',
          'add_order: cursor = conn.execute("INSERT … VALUES (?, ?)", (customer_id, amount)); return cursor.lastrowid.',
        ],
        tests: [
          { name: 'total_revenue sums everything', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            assert abs(total_revenue(_c) - 655.5) < 1e-6, f"Got {total_revenue(_c)!r}, expected 655.5"` },
          { name: 'orders_by_city joins and groups', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            _r = [(city, round(t, 2)) for city, t in orders_by_city(_c)]
            assert _r == [("Oslo", 325.5), ("Bergen", 310.0), ("Trondheim", 20.0)], f"Got {_r!r} — check the JOIN, GROUP BY and ORDER BY"` },
          { name: 'top_customers ranks correctly', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            _r = [(n, round(t, 2)) for n, t in top_customers(_c, 2)]
            assert _r == [("Linus", 310.0), ("Ada", 200.0)], f"Got {_r!r}"
            assert len(top_customers(_c, 10)) == 4, "Asking for more customers than exist returns everyone"` },
          { name: 'add_order inserts with parameters', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            _new = add_order(_c, 4, 99.5)
            assert isinstance(_new, int) and _new >= 8, f"Expected the new row id, got {_new!r}"
            assert abs(total_revenue(_c) - 755.0) < 1e-6, "The order should actually be inserted"
            _src = open("main.py").read()
            assert "?" in _src, "Use ? placeholders in add_order — no f-strings in SQL"` },
        ] },
      { id: 'be-2-3', type: 'quiz', title: 'Check: databases', min: 5, questions: [
        { q: 'A primary key…', opts: ['only speeds up SELECTs', 'uniquely identifies each row', 'stores passwords', 'is optional decoration'], a: 1, why: 'It is the row’s identity — and what foreign keys point at.' },
        { q: '`UPDATE users SET city = "Oslo"` without a WHERE…', opts: ['updates nothing', 'is an error', 'updates every row', 'updates the first row'], a: 2, why: 'No WHERE means all rows. Type the WHERE first.' },
        { q: 'Which query gets the 5 priciest items?', opts: ['SELECT * FROM items SORT price TOP 5', 'SELECT * FROM items ORDER BY price DESC LIMIT 5', 'SELECT TOP 5 FROM items', 'SELECT * FROM items WHERE price = MAX'], a: 1, why: 'ORDER BY … DESC sorts, LIMIT caps.' },
        { q: '`JOIN orders ON orders.customer_id = customers.id` does what?', opts: ['copies one table into another', 'combines rows from both tables where the keys match', 'deletes orphaned rows', 'renames columns'], a: 1, why: 'The ON condition says which rows belong together.' },
        { q: 'The `?` placeholders exist to…', opts: ['shorten queries', 'send values separately from the SQL so input can never become code', 'speed up SELECTs', 'format numbers'], a: 1, why: 'That separation is the whole defence against SQL injection.' },
        { q: 'An index on a column…', opts: ['makes every query faster', 'speeds up lookups on that column, at a small cost to writes', 'is required for SELECT', 'encrypts the column'], a: 1, why: 'Index what you filter and join on; skip the rest.' },
      ] },
    ] },
    { title: 'Auth and security', desc: 'Passwords, sessions, injection.', lessons: [
      { id: 'be-3-1', type: 'read', title: 'Authentication and the security basics', min: 13, md: 'be-3-1' },
      { id: 'be-3-2', type: 'code', title: 'Hash it, don’t store it', min: 16, lang: 'python', md: 'be-3-2.md',
        files: [{ name: 'main.py', key: 'be-3-2.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'be-3-2.solution.main.py' }],
        hints: [
          'salt = secrets.token_hex(16), then hashlib.sha256((salt + password).encode()).hexdigest().',
          'verify: salt, expected = stored.split("$", 1) — then redo the same hash and compare.',
        ],
        tests: [
          { name: 'Verifies the right password', code: `
            _s = hash_password("hunter2")
            assert verify_password("hunter2", _s) is True, "The correct password should verify"` },
          { name: 'Rejects the wrong password', code: `
            _s = hash_password("hunter2")
            assert verify_password("Hunter2", _s) is False, "Verification is exact — case matters"
            assert verify_password("", _s) is False, "The empty string is not the password"` },
          { name: 'Fresh salt every time', code: `
            assert hash_password("hunter2") != hash_password("hunter2"), "Two hashes of the same password must differ — generate a new salt on every call"` },
          { name: 'salt$hash format, no plaintext', code: `
            _s = hash_password("topsecret")
            assert "$" in _s and "topsecret" not in _s, f"Got {_s!r} — the stored string must not contain the password"
            _salt, _h = _s.split("$", 1)
            assert len(_salt) == 32 and len(_h) == 64, "token_hex(16) gives 32 hex chars; sha256 hexdigest gives 64"` },
        ] },
      { id: 'be-3-3', type: 'code', title: 'Close the injection hole', min: 16, lang: 'python', md: 'be-3-3.md', packages: ['sqlite3'],
        files: [{ name: 'main.py', key: 'be-3-3.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'be-3-3.solution.main.py' }],
        hints: [
          'The whole fix: conn.execute("SELECT name, email FROM users WHERE name = ?", (username,)) — note the 1-tuple.',
          'create_user: validate, execute the INSERT with two parameters, conn.commit(), return cursor.lastrowid.',
        ],
        tests: [
          { name: 'Finds an exact user', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            assert find_user(_c, "ada") == ("ada", "ada@example.com"), f"Got {find_user(_c, 'ada')!r}"
            assert find_user(_c, "nobody") is None, "Unknown users give None"` },
          { name: 'The injection comes back empty', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            assert find_user(_c, "' OR '1'='1") is None, "The glued SQL is still executing — use a ? parameter"` },
          { name: 'create_user inserts and returns an id', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            _id = create_user(_c, "ken", "ken@example.com")
            assert isinstance(_id, int), f"Return the new row id (got {_id!r})"
            assert find_user(_c, "ken") == ("ken", "ken@example.com"), "The user should actually be inserted"` },
          { name: 'create_user validates its input', code: `
            import sqlite3 as _sq
            _c = _sq.connect(":memory:")
            setup(_c)
            for _bad in [("", "a@b.com"), ("   ", "a@b.com"), ("bo", "not-an-email")]:
                try:
                    create_user(_c, _bad[0], _bad[1])
                    assert False, f"create_user{_bad!r} should raise ValueError"
                except ValueError:
                    pass` },
        ] },
      { id: 'be-3-4', type: 'quiz', title: 'Check: security', min: 5, questions: [
        { q: 'Databases store password hashes because…', opts: ['hashes are smaller', 'a hash can be checked but not reversed into the password', 'hashes load faster', 'regulations require SHA'], a: 1, why: 'A leak then exposes fingerprints, not credentials.' },
        { q: 'A salt…', opts: ['makes hashing faster', 'makes identical passwords produce different hashes, defeating precomputed tables', 'encrypts the database', 'is the username'], a: 1, why: 'Random per-user salt means attackers cannot precompute or spot shared passwords.' },
        { q: 'The input `\' OR \'1\'=\'1` is dangerous when…', opts: ['it is longer than 20 characters', 'the query is built by gluing strings, so the input becomes part of the SQL', 'always, even with parameters', 'only in Python'], a: 1, why: 'With ? parameters the same input is just a strange username.' },
        { q: 'bcrypt / argon2 beat plain sha256 for passwords because…', opts: ['they produce shorter hashes', 'they are deliberately slow, making mass guessing expensive', 'sha256 is broken for files', 'they need no salt'], a: 1, why: 'Fast is a feature everywhere except password hashing.' },
        { q: 'Where do API keys belong?', opts: ['as constants in the source', 'committed in config.json', 'in environment variables or a secret store, out of git', 'in the README'], a: 2, why: 'Anything committed is effectively public forever.' },
        { q: 'The server checks `Authorization: Bearer <token>` by…', opts: ['asking the user', 'verifying the token signature or looking up the session', 're-hashing the URL', 'checking the IP address'], a: 1, why: 'Signed token or server-side session — those are the two families.' },
      ] },
    ] },
    { title: 'Frameworks and deployment', desc: 'From handler to hosted service.', lessons: [
      { id: 'be-4-1', type: 'read', title: 'Flask, FastAPI, Express — and shipping it', min: 13, md: 'be-4-1' },
      { id: 'be-4-2', type: 'quiz', title: 'Check: frameworks & deployment', min: 4, questions: [
        { q: 'A framework like FastAPI or Express mainly…', opts: ['replaces the database', 'parses HTTP and routes requests to your functions', 'writes your business logic', 'hosts the app'], a: 1, why: 'You wrote the routing yourself in module 1 — the framework industrialises it.' },
        { q: '`DATABASE_URL` should come from…', opts: ['a constant in code', 'the environment (env vars / platform config)', 'the README', 'the client'], a: 1, why: 'Config differs per machine; the environment is where it lives.' },
        { q: 'A `/health` endpoint exists so that…', opts: ['users can log in', 'monitors and load balancers can tell the app is alive', 'the cache stays warm', 'the database resets'], a: 1, why: 'A cheap 200 that answers: is it up?' },
        { q: 'Docker’s job is…', opts: ['a faster Python', 'packaging the app with its exact dependencies so it runs the same everywhere', 'free hosting', 'automatic scaling'], a: 1, why: '"Works on my machine" becomes "ships as my machine".' },
        { q: 'FastAPI with pydantic models gives you…', opts: ['free HTML pages', 'request validation and interactive docs generated from your types', 'a database', 'authentication'], a: 1, why: 'Declare the shape once; bad requests never reach your code.' },
      ] },
    ] },
    { title: 'Project', desc: 'A real API, cleanly split.', lessons: [
      { id: 'be-5-1', type: 'project', title: 'Project: bookstore API', min: 60, lang: 'python', md: 'be-5-1.md', packages: ['sqlite3'],
        files: [
          { name: 'db.py', key: 'be-5-1.starter.db.py' },
          { name: 'api.py', key: 'be-5-1.starter.api.py' },
          { name: 'main.py', key: 'be-5-1.starter.main.py' },
        ], main: 'main.py',
        solution: [
          { name: 'db.py', key: 'be-5-1.solution.db.py' },
          { name: 'api.py', key: 'be-5-1.solution.api.py' },
          { name: 'main.py', key: 'be-5-1.solution.main.py' },
        ],
        hints: [
          'Split the query string first: path, _, query = path.partition("?").',
          'row_to_book keeps tuple-index juggling in exactly one place.',
          'One validate(body) returning an error string or None serves both POST and PUT.',
          'purchase is a sub-route: parts == ["books", "<id>", "purchase"] — check it before the plain /books/<id> block.',
          'The author filter: WHERE LOWER(author) = LOWER(?) — one parameter, injection-proof.',
        ],
        tests: [
          { name: 'init_db creates the table (twice is fine)', code: `
            import sqlite3 as _sq
            from db import init_db
            _c = _sq.connect(":memory:")
            init_db(_c)
            init_db(_c)
            _c.execute("SELECT id, title, author, price, stock FROM books")` },
          { name: 'POST creates; GET lists in id order', code: `
            import sqlite3 as _sq
            from db import init_db
            from api import handle_request
            _c = _sq.connect(":memory:")
            init_db(_c)
            _s1, _b1 = handle_request(_c, "POST", "/books", {"title": "The Dispossessed", "author": "Le Guin", "price": 129.0, "stock": 3})
            assert _s1 == 201 and _b1.get("id") and _b1["stock"] == 3, f"Got {(_s1, _b1)!r}"
            handle_request(_c, "POST", "/books", {"title": "Kindred", "author": "Butler", "price": 149.0, "stock": 2})
            _s2, _list = handle_request(_c, "GET", "/books")
            assert _s2 == 200 and [b["title"] for b in _list] == ["The Dispossessed", "Kindred"], f"Got {_list!r}"` },
          { name: 'POST validates every field', code: `
            import sqlite3 as _sq
            from db import init_db
            from api import handle_request
            _c = _sq.connect(":memory:")
            init_db(_c)
            for _bad in [{}, {"title": "", "author": "x", "price": 1, "stock": 1}, {"title": "x", "author": "y", "price": -1, "stock": 1}, {"title": "x", "author": "y", "price": 1, "stock": "many"}]:
                _s, _e = handle_request(_c, "POST", "/books", _bad)
                assert _s == 400 and "error" in _e, f"{_bad!r} should give 400, got {(_s, _e)!r}"` },
          { name: 'GET and DELETE by id, with 404s', code: `
            import sqlite3 as _sq
            from db import init_db
            from api import handle_request
            _c = _sq.connect(":memory:")
            init_db(_c)
            _b = handle_request(_c, "POST", "/books", {"title": "Dune", "author": "Herbert", "price": 99.0, "stock": 1})[1]
            _id = str(_b["id"])
            assert handle_request(_c, "GET", "/books/" + _id)[0] == 200
            assert handle_request(_c, "GET", "/books/424242")[0] == 404, "Unknown ids give 404"
            assert handle_request(_c, "DELETE", "/books/" + _id) == (204, None), "DELETE answers (204, None)"
            assert handle_request(_c, "GET", "/books/" + _id)[0] == 404, "The deleted book is gone"` },
          { name: 'PUT replaces after validating', code: `
            import sqlite3 as _sq
            from db import init_db
            from api import handle_request
            _c = _sq.connect(":memory:")
            init_db(_c)
            _b = handle_request(_c, "POST", "/books", {"title": "Dune", "author": "Herbert", "price": 99.0, "stock": 1})[1]
            _s, _u = handle_request(_c, "PUT", "/books/" + str(_b["id"]), {"title": "Dune", "author": "Herbert", "price": 129.0, "stock": 4})
            assert _s == 200 and _u["price"] == 129.0 and _u["stock"] == 4, f"Got {(_s, _u)!r}"
            assert handle_request(_c, "PUT", "/books/" + str(_b["id"]), {"title": ""})[0] == 400, "PUT validates like POST"
            assert handle_request(_c, "PUT", "/books/424242", {"title": "x", "author": "y", "price": 1, "stock": 1})[0] == 404` },
          { name: 'Author filter: case-insensitive, injection-proof', code: `
            import sqlite3 as _sq
            from db import init_db
            from api import handle_request
            _c = _sq.connect(":memory:")
            init_db(_c)
            handle_request(_c, "POST", "/books", {"title": "The Dispossessed", "author": "Le Guin", "price": 129.0, "stock": 3})
            handle_request(_c, "POST", "/books", {"title": "The Left Hand of Darkness", "author": "Le Guin", "price": 119.0, "stock": 2})
            handle_request(_c, "POST", "/books", {"title": "Kindred", "author": "Butler", "price": 149.0, "stock": 2})
            _s, _hits = handle_request(_c, "GET", "/books?author=LE GUIN")
            assert _s == 200 and len(_hits) == 2, f"Case-insensitive filter should find 2, got {_hits!r}"
            _s2, _inj = handle_request(_c, "GET", "/books?author=' OR '1'='1")
            assert _s2 == 200 and _inj == [], "The injection string is just a weird author name — expected an empty list"` },
          { name: 'Purchase reduces stock; 409 when short', code: `
            import sqlite3 as _sq
            from db import init_db
            from api import handle_request
            _c = _sq.connect(":memory:")
            init_db(_c)
            _b = handle_request(_c, "POST", "/books", {"title": "Dune", "author": "Herbert", "price": 99.0, "stock": 3})[1]
            _p = "/books/" + str(_b["id"]) + "/purchase"
            _s, _u = handle_request(_c, "POST", _p, {"quantity": 2})
            assert _s == 200 and _u["stock"] == 1, f"Got {(_s, _u)!r}"
            assert handle_request(_c, "POST", _p, {"quantity": 5})[0] == 409, "Buying more than the stock gives 409"
            assert handle_request(_c, "POST", _p, {"quantity": 0})[0] == 400, "quantity must be a positive integer"
            assert handle_request(_c, "POST", "/books/424242/purchase", {"quantity": 1})[0] == 404` },
        ] },
    ] },
  ],
},
{
  id: 'cs', name: 'Data Structures & Algorithms', icon: '🧠', tint: '#F1E8FB', fg: '#6A3BB5',
  tagline: 'The ideas behind fast, correct code.',
  outcomes: [
    'Judge code by its Big O shape',
    'Pick the right structure: stack, queue, set, map',
    'Implement binary search that is actually O(log n)',
    'Use recursion with a safe base case',
    'Make slow code fast with memoization',
  ],
  modules: [
    { title: 'Thinking in structures', desc: 'Complexity, structures, recursion.', lessons: [
      { id: 'cs-1-1', type: 'read', title: 'Big O and why it matters', min: 10, md: 'cs-1-1' },
      { id: 'cs-1-2', type: 'code', title: 'Binary search', min: 16, lang: 'python', md: 'cs-1-2.md',
        files: [{ name: 'main.py', key: 'cs-1-2.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'cs-1-2.solution.main.py' }],
        hints: [
          'while low <= high: mid = (low + high) // 2.',
          'items[mid] < target → the answer is right of mid: low = mid + 1. Too big → high = mid - 1.',
          'Only ever read items[mid] — anything that scans (in, .index, loops) fails the efficiency check.',
        ],
        tests: [
          { name: 'Finds every present value', code: `
            _xs = [1, 3, 5, 7, 9, 11]
            assert [binary_search(_xs, v) for v in _xs] == [0, 1, 2, 3, 4, 5], "Each value should map to its index"` },
          { name: 'Absent values give -1', code: `
            assert binary_search([1, 3, 5], 4) == -1, "4 is not in the list"
            assert binary_search([], 7) == -1, "The empty list has nothing"
            assert binary_search([5], 4) == -1 and binary_search([5], 5) == 0, "Single-element lists work too"` },
          { name: 'Handles the ends of a big list', code: `
            _big = list(range(0, 200000, 2))
            assert binary_search(_big, 0) == 0, "First element"
            assert binary_search(_big, 199998) == 99999, "Last element"
            assert binary_search(_big, 3) == -1, "Odd numbers are absent"` },
          { name: 'Actually O(log n)', code: `
            class _Probe:
                def __init__(self, n):
                    self.n = n
                    self.reads = 0
                def __len__(self):
                    return self.n
                def __getitem__(self, i):
                    if not isinstance(i, int):
                        raise TypeError("index must be an int")
                    if i < 0 or i >= self.n:
                        raise IndexError(i)
                    self.reads += 1
                    return i * 2
            _p = _Probe(100000)
            assert binary_search(_p, 135790) == 67895, "The probe list is 0, 2, 4, ... — 135790 sits at index 67895"
            assert _p.reads <= 25, f"Looked at {_p.reads} elements for n=100000 — halve the window each step (about 17 reads)"` },
        ] },
      { id: 'cs-1-3', type: 'read', title: 'Stacks, queues, hash maps, recursion', min: 12, md: 'cs-1-3' },
      { id: 'cs-1-4', type: 'code', title: 'Balanced brackets', min: 14, lang: 'python', md: 'cs-1-4.md',
        files: [{ name: 'main.py', key: 'cs-1-4.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'cs-1-4.solution.main.py' }],
        hints: [
          'Openers: push. Closers: the stack top must be pairs[char] — pop it, otherwise return False.',
          'A closer with an empty stack is an instant False; leftovers at the end mean unclosed brackets.',
        ],
        tests: [
          { name: 'Balanced strings pass', code: `
            for _s in ["", "()", "(a[b]{c})", "no brackets", "([]{})()"]:
                assert is_balanced(_s) is True, f"is_balanced({_s!r}) should be True"` },
          { name: 'Wrong closers fail', code: `
            for _s in ["(]", "([)]", "{(})"]:
                assert is_balanced(_s) is False, f"is_balanced({_s!r}) should be False — the closer must match the most recent opener"` },
          { name: 'Unclosed and unopened fail', code: `
            for _s in ["(()", ")(", "]", "((("]:
                assert is_balanced(_s) is False, f"is_balanced({_s!r}) should be False"` },
          { name: 'Ignores everything else', code: `
            assert is_balanced("def f(x): return [x] * {1: 2}[1]") is True, "Non-bracket characters are just scenery"` },
        ] },
      { id: 'cs-1-5', type: 'code', title: 'Fibonacci, fast and slow', min: 16, lang: 'python', md: 'cs-1-5.md',
        files: [{ name: 'main.py', key: 'cs-1-5.starter.main.py' }], main: 'main.py',
        solution: [{ name: 'main.py', key: 'cs-1-5.solution.main.py' }],
        hints: [
          'fib_naive: if n < 2: return n, then return fib_naive(n - 1) + fib_naive(n - 2).',
          'Iterative fib: a, b = 0, 1, then n times: a, b = b, a + b — return a.',
          'Or decorate the recursion with @lru_cache from functools.',
        ],
        tests: [
          { name: 'Both agree on the sequence', code: `
            _e = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
            assert [fib(n) for n in range(10)] == _e, f"fib gave {[fib(n) for n in range(10)]!r}"
            assert [fib_naive(n) for n in range(10)] == _e, f"fib_naive gave {[fib_naive(n) for n in range(10)]!r}"` },
          { name: 'fib_naive is the plain recursion', code: `
            _src = open("main.py").read()
            assert _src.count("fib_naive(") >= 3, "fib_naive should call itself twice — the point is to feel the O(2^n)"` },
          { name: 'fib(90) is instant and exact', code: `
            import time as _t
            _start = _t.time()
            _v = fib(90)
            _dt = _t.time() - _start
            assert _v == 2880067194370816120, f"fib(90) gave {_v!r}"
            assert _dt < 0.5, f"fib(90) took {_dt:.2f}s — iterate or memoize instead of recomputing"` },
        ] },
      { id: 'cs-1-6', type: 'quiz', title: 'Check: algorithms', min: 5, questions: [
        { q: 'A loop inside a loop over the same n items is…', opts: ['O(n)', 'O(2n)', 'O(n²)', 'O(log n)'], a: 2, why: 'n passes of n work each: n².' },
        { q: '`x in my_set` vs `x in my_list`…', opts: ['both O(1)', 'set is O(1); list is O(n)', 'list is O(1); set is O(n)', 'both O(n)'], a: 1, why: 'Sets hash; lists scan. The most common real-world speedup there is.' },
        { q: 'Binary search requires the data to be…', opts: ['unique', 'sorted', 'numeric', 'short'], a: 1, why: 'Halving only works when order tells you which half to keep.' },
        { q: 'Which structure fits an undo feature?', opts: ['queue', 'stack', 'set', 'tree'], a: 1, why: 'Undo takes the most recent action first: last in, first out.' },
        { q: 'Every recursive function needs…', opts: ['a loop', 'a base case that every call moves toward', 'global state', 'exactly two recursive calls'], a: 1, why: 'Without it: RecursionError — the stack’s version of an infinite loop.' },
        { q: 'Memoization speeds things up by…', opts: ['compiling to C', 'caching subproblem results so each is computed once', 'skipping the base case', 'running in parallel'], a: 1, why: 'fib collapses from O(2ⁿ) to O(n) — same maths, no repeats.' },
      ] },
    ] },
  ],
},
{
  id: 'tools', name: 'Developer Toolkit', icon: '🧰', tint: '#FFF3D6', fg: '#8A6400',
  tagline: 'Git, the terminal, testing and debugging — habits that make projects survive.',
  outcomes: [
    'Version work with git: commit, branch, merge, push',
    'Move around a terminal without fear',
    'Manage dependencies with pip and npm',
    'Write pytest tests that guard your code',
    'Debug with a method instead of guesses',
  ],
  modules: [
    { title: 'The working craft', desc: 'The tools around the code.', lessons: [
      { id: 'tools-1-1', type: 'read', title: 'Git in one sitting', min: 13, md: 'tools-1-1' },
      { id: 'tools-1-2', type: 'read', title: 'Terminal, packages and project layout', min: 11, md: 'tools-1-2' },
      { id: 'tools-1-3', type: 'read', title: 'Testing and debugging', min: 12, md: 'tools-1-3' },
      { id: 'tools-1-4', type: 'quiz', title: 'Check: toolkit', min: 5, questions: [
        { q: 'The everyday git rhythm is…', opts: ['clone → push → merge', 'status → add → commit', 'init → delete → init', 'branch → branch → branch'], a: 1, why: 'See what changed, stage it, snapshot it — several times a day.' },
        { q: '`.gitignore` is for…', opts: ['files git must encrypt', 'files that should stay out of history: venv, node_modules, .env, build output', 'the main branch', 'large images only'], a: 1, why: 'Especially .env — secrets in git history are effectively public.' },
        { q: 'A merge conflict means…', opts: ['the repository is corrupted', 'both branches changed the same lines; you edit the file, add, and commit', 'you must delete a branch', 'git chose randomly'], a: 1, why: 'Normal teamwork, not an emergency. The markers show you both versions.' },
        { q: '`requirements.txt` / `package.json` exist so that…', opts: ['the app runs faster', 'anyone (including future you) can recreate the exact dependency set', 'git can work', 'Python finds main.py'], a: 1, why: 'The environment becomes reproducible instead of folklore.' },
        { q: 'A test you wrote for a bug you fixed…', opts: ['should be deleted after the fix', 'stays forever so the bug can never quietly return', 'proves tests are pointless', 'must be skipped in CI'], a: 1, why: 'That is a regression test — the compound interest of testing.' },
        { q: 'The first step when you hit a bug?', opts: ['rewrite the module', 'reproduce it with the smallest input that triggers it', 'wrap everything in try/except', 'restart the computer'], a: 1, why: 'A reliable reproduction is half the fix; many bugs dissolve while you build one.' },
      ] },
    ] },
  ],
},
];
