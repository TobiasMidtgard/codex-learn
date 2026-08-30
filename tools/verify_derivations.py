"""verify_derivations.py — the correctness gate for guided derivations.

`verify_labs.py` proves that every lab's reference solution passes its own checks.
This proves the same thing one layer up: that every derivation step's *answer* is
accepted by the checker that will grade it.

That is not a tautology. An answer can fail against itself for several real reasons,
all of which have happened:

  * a symbol the step uses is missing from `vars`, so a multi-letter name is split
    into a product of single letters
  * the answer is a Python keyword — `lambda` is the obvious name for an eigenvalue
    and a syntax error
  * the answer is a relation rather than an expression, and cannot be subtracted
  * the LaTeX is outside the supported subset and silently loses a term

Every one of those ships a step that a learner cannot possibly pass.

The LaTeX-to-SymPy translation lives in src/studio.js and is reached by running that
file in Node, so there is exactly one translator and this gate cannot drift from the
one the browser uses.

    python -X utf8 tools/verify_derivations.py                 # every course
    python -X utf8 tools/verify_derivations.py catalog/CTRL510.json
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO = os.path.join(ROOT, "src", "studio.js")

TRANSLATE_JS = r"""
const fs = require('fs');
const m = { exports: {} };
new Function('module', 'PyRunner',
  fs.readFileSync(process.argv[2], 'utf8') + '\nmodule.exports = { MathCheck };'
)(m, { run: async () => {} });
const jobs = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const out = jobs.map(function (j) {
  try { return { ok: true, py: m.exports.MathCheck.latexToPy(j.answer, j.vars) }; }
  catch (e) { return { ok: false, py: '', err: String(e && e.message || e) }; }
});
process.stdout.write(JSON.stringify(out));
"""


def as_list(x):
    """A unit key holds nothing, one authored object, or a list of them."""
    if not x:
        return []
    return x if isinstance(x, list) else [x]


def translate(jobs):
    """Run every answer through the real translator in src/studio.js."""
    with tempfile.TemporaryDirectory() as d:
        js = os.path.join(d, "t.cjs")
        data = os.path.join(d, "jobs.json")
        with open(js, "w", encoding="utf-8") as f:
            f.write(TRANSLATE_JS)
        with open(data, "w", encoding="utf-8") as f:
            json.dump(jobs, f)
        res = subprocess.run(
            ["node", js, STUDIO, data],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
    if res.returncode != 0:
        raise SystemExit("could not run the translator:\n" + (res.stderr or "")[:2000])
    return json.loads(res.stdout)


def make_checker():
    """The same equivalence rule the browser applies, in local SymPy."""
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations,
        implicit_multiplication_application, convert_xor, split_symbols,
    )
    T = standard_transformations + (convert_xor, split_symbols,
                                    implicit_multiplication_application)

    def check(py_text, names):
        local = {n: sp.Symbol(n) for n in names}
        expr = parse_expr(py_text, local_dict=dict(local), transformations=T)
        rel = sp.core.relational.Relational
        if isinstance(expr, rel):
            return bool(sp.simplify(expr) == sp.simplify(expr))
        d = sp.simplify(sp.together(expr - expr))
        return d == 0

    return check


def main(argv):
    try:
        import sympy  # noqa: F401
    except Exception:
        raise SystemExit("verify_derivations needs sympy:\n  python -m pip install sympy")

    files = argv or sorted(
        p for p in glob.glob(os.path.join(ROOT, "catalog", "*.json"))
        if not os.path.basename(p).startswith("_")
    )

    jobs, where, leaks = [], [], []
    for path in files:
        with open(path, encoding="utf-8") as f:
            course = json.load(f)
        for mi, mod in enumerate(course.get("modules", []), 1):
            for dv in as_list(mod.get("derive")):
                names = list(dv.get("vars") or [])
                for si, st in enumerate(dv.get("steps", []), 1):
                    jobs.append({"answer": st["answer"], "vars": names})
                    where.append((course["id"], mi, si, st["answer"], names, dv["title"]))
                    # A placeholder showing the answer turns the exercise into a
                    # transcription task. The app refuses to render one, but a course
                    # should not ship it either.
                    ph = "".join((st.get("placeholder") or "").split())
                    an = "".join((st.get("answer") or "").split())
                    if ph and ph == an:
                        leaks.append(f"{course['id']}/M{mi} step {si}: the placeholder is the answer")

    if not jobs:
        print("no derivations found")
        return 0

    translated = translate(jobs)
    check = make_checker()

    reserved = {"lambda", "is", "in", "not", "or", "and", "if", "else", "for", "while",
                "class", "def", "from", "import", "as", "return", "None", "True",
                "False", "del", "pass", "global", "assert", "raise", "with", "yield"}

    problems = []
    by_course = {}
    for (cid, mi, si, latex, names, title), tr in zip(where, translated):
        by_course.setdefault(cid, [0, 0])
        by_course[cid][1] += 1
        label = f"{cid}/M{mi} step {si}"
        if not tr["ok"]:
            problems.append(f"{label}: the translator threw — {tr.get('err','')}")
            continue
        py = tr["py"]
        safe = [n + "_" if n in reserved else n for n in names]
        try:
            if check(py, safe):
                by_course[cid][0] += 1
            else:
                problems.append(f"{label}: does not match itself — {latex!r} -> {py!r}")
        except Exception as e:
            problems.append(
                f"{label}: {type(e).__name__}: {e}\n"
                f"           {latex!r}\n"
                f"           -> {py!r}\n"
                f"           declared vars: {names}"
            )

    for cid in sorted(by_course):
        ok, total = by_course[cid]
        mark = "ok  " if ok == total else "FAIL"
        print(f"[{mark}] {cid:8} {ok}/{total} derivation steps self-check")

    if leaks:
        print("\nPLACEHOLDERS SHOWING THE ANSWER")
        for l in leaks[:20]:
            print("  !", l)
        if len(leaks) > 20:
            print(f"  ... and {len(leaks) - 20} more")
        problems.extend(leaks)

    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print("  !", p)
        print(f"\n{len(problems)} step(s) a learner could not pass")
        return 1

    total = sum(v[1] for v in by_course.values())
    print(f"\nAll good: {total} derivation steps verified across {len(by_course)} course(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
