"""
verify_reads.py — every worked example in a reading unit actually runs.

A reading unit's fenced ```python blocks carry a Run button in the app, and each
one runs on its own, where it sits, in a fresh namespace. So a block that prints
the wrong thing, raises, or leans on a name defined three blocks earlier is a
defect the learner meets the moment they press the button — and no other gate
looks at reading units at all.

For every catalog/<ID>.json it walks modules[].read[] (a unit key holds nothing,
one object, or a list; iterate), pulls every fenced python block out of the body,
and executes each block standalone under CPython with stdout captured, in a child
process so a runaway loop costs one course rather than the gate:

  * a block passes when it raises nothing;
  * a REPL transcript — lines beginning `>>> ` and `... ` with the answers written
    between them — is run the way the app's Run button runs it: prompts stripped,
    answer lines dropped. The app and this gate share that rule on purpose, so a
    transcript that passes here is a transcript that runs there;
  * a block whose FIRST line is a comment containing `raises` is expected to raise
    — `# raises ZeroDivisionError` also checks the exception's name — and fails
    the gate if it runs clean, because a demonstration of an error that does not
    error is teaching the opposite of what it says;
  * imports outside the browser sandbox are refused, using verify_labs.py's list,
    for the same reason it refuses them in a lab;
  * the reading's word count is re-checked against emit.py's floor, because this
    reads the artifact the app serves rather than the source.

THE BUDGET. The EE first-year courses were written before this gate existed, in a
style that shows fragments — an `if` with its body left to the reader, a loop over
a name defined two blocks up. Those are 400-odd blocks that do not run standalone,
and rewriting them is a curriculum cycle's work rather than a gate's. So, as
tools/quiz_budget.json does for the question bank, tools/reads_budget.json records
what each course scores today and this gate fails when a course gets WORSE. A
course with no entry is held to zero, which is what every new reading is held to.

Usage
  python -X utf8 tools/verify_reads.py                     # every catalog/*.json
  python -X utf8 tools/verify_reads.py catalog/CS201.json  # named files
  python -X utf8 tools/verify_reads.py --verbose           # list every failure
  python -X utf8 tools/verify_reads.py --write-budget      # re-record the budget
"""

from __future__ import annotations

import glob
import io
import json
import os
import re
import subprocess
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from verify_labs import BANNED_IMPORTS  # noqa: E402

BUDGET = os.path.join(HERE, "reads_budget.json")
PER_COURSE_TIMEOUT = 240      # seconds, for every block of one course together
WORD_FLOOR = 400              # emit.py's floor, re-checked on the artifact
FENCE = re.compile(r"```([A-Za-z0-9_+-]*)[^\n]*\n(.*?)```", re.S)
RAISES = re.compile(r"^\s*#.*\braises\b(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?", re.I)
IMPORT = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w.]*)|import\s+([A-Za-z_][\w.]*))", re.M)


def as_list(x):
    if not x:
        return []
    return x if isinstance(x, list) else [x]


def transcript_to_code(code: str) -> str:
    """The app's rule for a `>>>` block, byte for byte (see runSnippet in app.js)."""
    lines = code.split("\n")
    if not any(line.lstrip().startswith(">>> ") or line.strip() == ">>>" for line in lines):
        return code
    out = []
    for line in lines:
        s = line.lstrip()
        if s.startswith(">>> "):
            out.append(s[4:])
        elif s == ">>>":
            out.append("")
        elif s.startswith("... "):
            out.append(s[4:])
        elif s == "...":
            out.append("")
        # anything else is the answer the transcript shows, not code
    return "\n".join(out)


def blocks_of(body: str):
    return [(lang.lower(), code) for lang, code in FENCE.findall(body)]


def banned_in(code: str):
    hits = set()
    for m in IMPORT.finditer(code):
        mod = (m.group(1) or m.group(2) or "").split(".")[0]
        if mod in BANNED_IMPORTS:
            hits.add(mod)
    return sorted(hits)


# ---------------------------------------------------------------- child
def run_blocks(payload: list) -> list:
    """Execute every block standalone. Runs in the child process."""
    results = []
    for item in payload:
        code = item["code"]
        expect = item["expect"]          # None, or "" (any), or an exception name
        ns = {"__name__": "__main__"}
        buf = io.StringIO()
        err = None
        raised = None
        try:
            with redirect_stdout(buf), redirect_stderr(io.StringIO()):
                exec(compile(code, "<example>", "exec"), ns)
        except SystemExit:
            pass
        except BaseException as e:      # noqa: BLE001 — the whole point is to see it
            raised = type(e).__name__
            err = "".join(traceback.format_exception_only(type(e), e)).strip().splitlines()[-1]
        if expect is None:
            ok = raised is None
        elif expect == "":
            ok = raised is not None
        else:
            ok = raised is not None and (raised == expect or expect.endswith("." + raised))
        results.append({"where": item["where"], "ok": ok, "raised": raised,
                        "expect": expect, "err": err})
    return results


def child_main():
    payload = json.load(sys.stdin)
    print(json.dumps(run_blocks(payload)))


# ---------------------------------------------------------------- parent
def check_course(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        course = json.load(fh)
    cid = course.get("id") or os.path.basename(path)
    hard = []          # structural: never budgeted
    failures = []      # blocks that do not run standalone: budgeted
    todo = []
    readings = 0
    fences = 0
    for mi, m in enumerate(course.get("modules") or [], 1):
        for ri, u in enumerate(as_list(m.get("read")), 1):
            readings += 1
            where = f"{cid}/M{mi}/read{ri}"
            body = u.get("body") or ""
            words = len(body.split())
            if words < WORD_FLOOR:
                hard.append(f"{where}: {words} words, under the {WORD_FLOOR}-word floor")
            for bi, (lang, code) in enumerate(blocks_of(body), 1):
                if lang not in ("python", "py"):
                    continue
                fences += 1
                bwhere = f"{where} block {bi}"
                bad = banned_in(code)
                if bad:
                    hard.append(f"{bwhere}: imports {', '.join(bad)}, which the browser sandbox does not have")
                    continue
                first = code.split("\n", 1)[0]
                mr = RAISES.match(first)
                expect = (mr.group(1) or "") if mr else None
                todo.append({"where": bwhere, "code": transcript_to_code(code), "expect": expect})

    if todo:
        proc = None
        try:
            proc = subprocess.run(
                [sys.executable, "-X", "utf8", os.path.abspath(__file__), "--child"],
                input=json.dumps(todo), capture_output=True, text=True,
                encoding="utf-8", timeout=PER_COURSE_TIMEOUT, cwd=ROOT,
            )
        except subprocess.TimeoutExpired:
            hard.append(f"{cid}: the examples did not finish in {PER_COURSE_TIMEOUT}s — "
                        "a block is looping or waiting on input")
        if proc is not None:
            if proc.returncode != 0 or not proc.stdout.strip():
                tail = (proc.stderr or "").strip().splitlines()
                hard.append(f"{cid}: the example runner crashed: {tail[-1] if tail else 'no output'}")
            else:
                for r in json.loads(proc.stdout.strip().splitlines()[-1]):
                    if r["ok"]:
                        continue
                    if r["expect"] is None:
                        failures.append(f"{r['where']}: {r['err']}")
                    elif r["raised"] is None:
                        failures.append(f"{r['where']}: is marked `# raises` but ran clean")
                    else:
                        failures.append(f"{r['where']}: expected {r['expect']} but raised {r['raised']}")
    return {"id": cid, "readings": readings, "examples": fences, "hard": hard, "failures": failures}


def main(argv) -> int:
    if "--child" in argv:
        child_main()
        return 0
    verbose = "--verbose" in argv
    write = "--write-budget" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        paths = sorted(p for p in glob.glob(os.path.join(ROOT, "catalog", "*.json"))
                       if not os.path.basename(p).startswith("_"))
    budget = {}
    try:
        with open(BUDGET, encoding="utf-8") as fh:
            budget = json.load(fh)
    except (OSError, ValueError):
        budget = {}

    reports = [check_course(p) for p in paths]
    problems = 0
    for r in reports:
        allowed = int(budget.get(r["id"], 0))
        over = len(r["failures"]) > allowed
        bad = bool(r["hard"]) or over
        problems += bad
        mark = "FAIL" if bad else "ok  "
        print(f"[{mark}] {r['id']:<8} {r['readings']:>3} readings, {r['examples']:>4} python examples, "
              f"{len(r['failures']):>3} not standalone (budget {allowed})")
        for e in r["hard"]:
            print("      !", e)
        if over or verbose:
            for e in r["failures"]:
                print("      -", e)
    print()

    if write:
        merged = dict(budget)
        for r in reports:
            merged[r["id"]] = len(r["failures"])
        with open(BUDGET, "w", encoding="utf-8") as fh:
            json.dump(dict(sorted(merged.items())), fh, indent=1)
            fh.write("\n")
        print(f"budget written to {os.path.relpath(BUDGET, ROOT)}")

    tighter = [r for r in reports if len(r["failures"]) < int(budget.get(r["id"], 0))]
    if tighter and not write:
        print(f"{len(tighter)} course(s) now score BETTER than their budget — move the entries down: "
              + ", ".join(f"{r['id']} {len(r['failures'])}" for r in tighter))
    if problems:
        print(f"\n{problems} course(s) with a reading defect or over budget")
        return 1
    print(f"All good: {sum(r['examples'] for r in reports)} examples across "
          f"{sum(r['readings'] for r in reports)} readings in {len(reports)} course(s), "
          f"every course within its budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
