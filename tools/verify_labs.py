"""
verify_labs.py — prove every generated lab is real.

Replicates the Codewright Pyodide runner's semantics with local CPython:

  * starter/solution files are written to a scratch cwd (also on sys.path)
  * the `main` file is executed with a fresh globals dict whose __name__ is "__main__"
  * stdout is captured into the string `_out`
  * each test's code is then exec'd in that *same* namespace, with `_out` bound
  * a test "passes" when it raises nothing

For every lab it answers two questions:

  1. does the SOLUTION pass all of its own tests?   (must be yes)
  2. does the STARTER fail at least one test?       (must be yes, else the
                                                     exercise is pre-solved)

Usage
  python tools/verify_labs.py                     # every catalog/*.json
  python tools/verify_labs.py catalog/CS101.json  # named files
  python tools/verify_labs.py --json              # machine-readable summary
"""

from __future__ import annotations

import argparse
import glob
import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PER_LAB_TIMEOUT = 90  # seconds
SENTINEL = "<<<CW-LAB-RESULT>>>"  # not whitespace: str.strip() must not eat it

# Anything outside this set is unavailable (or ruinously slow) in the browser
# sandbox, so a lab that reaches for it would pass here and fail for a student.
# The old list lumped three different things together under one reason. They are
# not the same, and conflating them cost the EE curriculum its numerics.
#
#   1. absent from Pyodide entirely — a lab reaching for these dies in the browser
#   2. structurally impossible in WASM — no processes, no sockets, no native UI
#   3. present in the Pyodide distribution and auto-installed by
#      loadPackagesFromImports (engine.js) — these are FINE in a lab, provided the
#      local gate has them too, or this script would bless code it never ran.
#
# Anything in group 3 must be importable here. ALLOWED_HEAVY is checked at startup
# so a missing local install fails loudly instead of silently skipping the check.
BANNED_IMPORTS = {
    # 1. not in the distribution
    "torch", "tensorflow", "sklearn", "django", "flask", "fastapi", "pydantic",
    "cv2", "numba", "z3", "qiskit", "gym", "gymnasium", "gmpy2", "polars",
    "pyarrow", "nacl", "pytest",
    # 2. impossible in the browser sandbox
    "multiprocessing", "subprocess", "socket", "ctypes", "curses", "tkinter",
    "requests", "httpx", "aiohttp",
}

# group 3: allowed, but only because both gates can run them
ALLOWED_HEAVY = {"numpy", "sympy"}


# ---------------------------------------------------------------- dedent
def app_dedent(s: str) -> str:
    """Byte-for-byte port of the app's dedent() so tests see identical source."""
    s = str(s)
    i = 0
    while i < len(s) and s[i] == "\n":
        i += 1
    s = s[i:].rstrip()
    lines = s.split("\n")
    lo = None
    for line in lines:
        if not line.strip():
            continue
        n = len(line) - len(line.lstrip(" \t"))
        lo = n if lo is None else min(lo, n)
    if not lo:
        return "\n".join(lines)
    return "\n".join(line[lo:] for line in lines)


# ---------------------------------------------------------------- child
def run_one(payload: dict) -> dict:
    """Execute one lab variant in this process. Returns a result dict."""
    files = payload["files"]
    main = payload["main"]
    tests = payload["tests"]

    workdir = tempfile.mkdtemp(prefix="cwlab-")
    os.chdir(workdir)
    if workdir not in sys.path:
        sys.path.insert(0, workdir)

    for f in files:
        path = os.path.join(workdir, f["name"])
        os.makedirs(os.path.dirname(path) or workdir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(f["content"])

    main_src = next((f["content"] for f in files if f["name"] == main), None)
    if main_src is None:
        return {"ok": False, "fatal": f"main file {main!r} not among files", "tests": []}

    ns: dict = {"__name__": "__main__", "__file__": main}
    buf = io.StringIO()
    fatal = None
    try:
        with redirect_stdout(buf), redirect_stderr(io.StringIO()):
            # Pyodide runs the main file as a *string* compiled under the name
            # "<exec>", so inspect.getsource() cannot work there. Compile it the
            # same way, or this harness would bless labs that die in the browser.
            exec(compile(main_src, "<exec>", "exec"), ns)
    except SystemExit:
        pass
    except BaseException:
        fatal = traceback.format_exc(limit=6)

    ns["_out"] = buf.getvalue()

    results = []
    for t in tests:
        code = app_dedent(t["code"])
        tbuf = io.StringIO()
        try:
            with redirect_stdout(tbuf), redirect_stderr(io.StringIO()):
                exec(compile(code, "<test>", "exec"), ns)
            results.append({"name": t["name"], "pass": True})
        except BaseException as e:
            last = traceback.format_exc().strip().split("\n")[-1]
            results.append({"name": t["name"], "pass": False, "message": last})

    return {"ok": fatal is None, "fatal": fatal, "tests": results,
            "stdout": ns["_out"][:2000]}


# ---------------------------------------------------------------- parent
def spawn(payload: dict) -> dict:
    """Run one lab variant in a child process so hangs/crashes stay contained."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as fh:
        json.dump(payload, fh)
        pfile = fh.name
    try:
        proc = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--run", pfile],
            capture_output=True, text=True, timeout=PER_LAB_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "fatal": f"timed out after {PER_LAB_TIMEOUT}s "
                                      "(infinite loop, or far too slow)",
                "tests": []}
    finally:
        try:
            os.unlink(pfile)
        except OSError:
            pass

    out = proc.stdout
    start = out.rfind(SENTINEL)  # marker we emit immediately before the JSON
    if start == -1:
        return {"ok": False, "fatal": "child produced no result\n" + proc.stderr[-800:],
                "tests": []}
    try:
        return json.loads(out[start + len(SENTINEL):])
    except json.JSONDecodeError as e:
        return {"ok": False, "fatal": f"unreadable child result: {e}", "tests": []}


def overlay(starter, solution):
    """Solution files replace same-named starter files; the rest carry over."""
    by_name = {f["name"]: dict(f) for f in starter}
    for f in solution or []:
        by_name[f["name"]] = dict(f)
    return list(by_name.values())


# Present in CPython but missing (or ruinously slow) in Pyodide's WASM build.
# CPython would happily verify a lab that then dies in the student's browser, so
# these are matched by name anywhere in executable code.
BANNED_ATTRS = {
    "pbkdf2_hmac": "hashlib.pbkdf2_hmac does not exist in Pyodide — write the "
                   "PBKDF2 loop out with hmac + sha256",
    "hashlib.scrypt": "hashlib.scrypt is unavailable in Pyodide",
    "hashlib.blake2b": "blake2 is unavailable in some Pyodide builds",
    "os.fork": "no process control in the browser",
    "time.process_time": "unreliable in Pyodide",
}


def banned_used(files):
    hits = set()
    for f in files:
        src = f["content"]
        for mod in BANNED_IMPORTS:
            for pat in (f"import {mod}", f"from {mod}"):
                if pat in src:
                    hits.add(mod)
        for attr, why in BANNED_ATTRS.items():
            # match a call, not a mention: a docstring may legitimately name it
            if (attr + "(") in src:
                hits.add(f"{attr} ({why})")
    return sorted(hits)


def as_list(x):
    """A unit key holds nothing, one authored object, or a list of them."""
    if not x:
        return []
    return x if isinstance(x, list) else [x]


def iter_labs(course):
    for mi, module in enumerate(course.get("modules", [])):
        labs = as_list(module.get("lab"))
        for li, lab in enumerate(labs, 1):
            tag = f"M{mi + 1}" if len(labs) == 1 else f"M{mi + 1}.{li}"
            yield tag, module.get("title", ""), lab
    cap = course.get("capstone")
    if cap and cap.get("tests"):
        yield "CAP", "Capstone", cap


def check_course(path) -> dict:
    with open(path, encoding="utf-8") as fh:
        course = json.load(fh)

    cid = course.get("id", os.path.basename(path))
    report = {"id": cid, "path": path, "labs": [], "errors": [], "notes": []}

    for tag, mtitle, lab in iter_labs(course):
        name = f"{cid}/{tag}"
        entry = {"lab": name, "title": lab.get("title", mtitle)}

        if lab.get("runtime", "python") != "python":
            entry["skipped"] = f"runtime={lab.get('runtime')} (not CPython-verifiable)"
            report["labs"].append(entry)
            continue

        starter = lab.get("files") or []
        solution = lab.get("solution") or []
        tests = lab.get("tests") or []

        if not tests:
            entry["error"] = "no tests"
            report["labs"].append(entry)
            report["errors"].append(f"{name}: no tests")
            continue

        bad = banned_used(overlay(starter, solution) +
                          [{"name": "<test>", "content": t["code"]} for t in tests])
        if bad:
            entry["error"] = f"uses unavailable module(s): {', '.join(bad)}"
            report["errors"].append(f"{name}: unavailable import {bad}")

        sol = spawn({"files": overlay(starter, solution),
                     "main": lab["main"], "tests": tests})
        entry["solution"] = sol
        failed = [t for t in sol["tests"] if not t["pass"]]
        if sol.get("fatal"):
            report["errors"].append(f"{name}: solution crashed — "
                                    f"{sol['fatal'].splitlines()[-1] if sol['fatal'] else ''}")
        if failed:
            for t in failed:
                report["errors"].append(f"{name}: solution fails check "
                                        f"{t['name']!r} — {t.get('message', '')}")

        st = spawn({"files": starter, "main": lab["main"], "tests": tests})
        entry["starter"] = st
        st_failed = [t for t in st["tests"] if not t["pass"]]
        st_passed = [t for t in st["tests"] if t["pass"]]
        if not st_failed and not st.get("fatal"):
            entry["warning"] = "starter already passes every check"
            report["errors"].append(f"{name}: starter is pre-solved")
        elif st_passed:
            # A check the stub already satisfies teaches nothing, whether or not the
            # others fail. Only reporting the all-pass case let a single vacuous check
            # hide inside a "starter 1/7" that nobody reads: usually an assertion about
            # an absence, or a division by a stubbed zero producing inf.
            entry["hollow"] = [t["name"] for t in st_passed]
            report["notes"].append(
                f"{name}: the starter already passes "
                + ", ".join(repr(t["name"]) for t in st_passed)
                + " — check that assertion is not satisfied by the stub"
            )

        entry["summary"] = (f"solution {len(sol['tests']) - len(failed)}/{len(sol['tests'])}"
                            f" · starter {len(st['tests']) - len(st_failed)}/{len(st['tests'])}")
        report["labs"].append(entry)

    return report


def check_local_env() -> None:
    """The two-gate property only holds if this gate can run what the browser runs.
    A lab importing numpy would otherwise be silently unverifiable here."""
    import importlib
    missing = []
    for mod in sorted(ALLOWED_HEAVY):
        try:
            importlib.import_module(mod)
        except Exception:
            missing.append(mod)
    if missing:
        raise SystemExit(
            "verify_labs needs " + ", ".join(missing) + " locally, because labs are "
            "allowed to import them and the browser can.\n"
            "  python -m pip install " + " ".join(missing)
        )


def main():
    check_local_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--run", help=argparse.SUPPRESS)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.run:
        with open(args.run, encoding="utf-8") as fh:
            payload = json.load(fh)
        result = run_one(payload)
        sys.stdout.write(SENTINEL + json.dumps(result))
        return 0

    paths = args.paths or sorted(
        p for p in glob.glob(os.path.join(ROOT, "catalog", "*.json"))
        if not os.path.basename(p).startswith("_")
    )
    if not paths:
        print("no catalog files found")
        return 1

    reports = [check_course(p) for p in paths]
    all_errors = [e for r in reports for e in r["errors"]]
    all_notes = [n for r in reports for n in r.get("notes", [])]

    if args.json:
        print(json.dumps({"reports": reports, "errors": all_errors}, indent=1))
    else:
        for r in reports:
            mark = "FAIL" if r["errors"] else "ok  "
            print(f"[{mark}] {r['id']:<8} {len(r['labs'])} labs")
            for lab in r["labs"]:
                if lab.get("skipped"):
                    print(f"        - {lab['lab']:<14} skipped: {lab['skipped']}")
                else:
                    flag = "!" if lab.get("error") or lab.get("warning") else " "
                    print(f"       {flag}  {lab['lab']:<14} {lab.get('summary', '')}"
                          f"{'  <' + lab['error'] + '>' if lab.get('error') else ''}"
                          f"{'  <' + lab['warning'] + '>' if lab.get('warning') else ''}")
        print()
        if all_errors:
            print(f"{len(all_errors)} problem(s):")
            for n in all_notes:
                print('  ?', n)
            for e in all_errors:
                print("  -", e)
        else:
            print(f"All good: {sum(len(r['labs']) for r in reports)} labs verified "
                  f"across {len(reports)} courses.")

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
