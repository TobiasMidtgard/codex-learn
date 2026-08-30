"""
emit.py — turn course *author modules* into catalog JSON.

Authoring a course as JSON means escaping every newline and quote of every code
sample. Authoring it as a Python module lets you write code in r'''...''' blocks
exactly as a student will see it. This script is the bridge.

An author module lives at catalog/authors/<COURSE_ID>.py and defines a single
top-level dict named COURSE.

Usage
  python tools/emit.py --all                     # every author module
  python tools/emit.py catalog/authors/CS101.py  # just one
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import math
import re
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AUTHORS = os.path.join(ROOT, "catalog", "authors")
OUT = os.path.join(ROOT, "catalog")

LEVELS = {"Beginner", "Intermediate", "Advanced", "Expert"}
RUNTIMES = {"python", "web", "js"}


def load_module(path):
    name = "course_" + os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clean_code(s: str) -> str:
    """Author modules indent nothing, but be forgiving; also normalise endings."""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n")
    if s.startswith("\n"):
        s = s[1:]
    return s.rstrip() + "\n"


def clean_md(s: str) -> str:
    s = str(s).replace("\r\n", "\n").replace("\r", "\n")
    return textwrap.dedent(s).strip()


def norm_files(files):
    return [{"name": f["name"], "content": clean_code(f["content"]),
             **({"ro": True} if f.get("ro") else {})} for f in files or []]


def norm_tests(tests):
    return [{"name": t["name"], "code": clean_md(t["code"])} for t in tests or []]


def norm_lab(lab, ctx):
    if not lab:
        return None
    out = {
        "title": lab["title"],
        "runtime": lab.get("runtime", "python"),
        "minutes": int(lab.get("minutes", 30)),
        "brief": clean_md(lab["brief"]),
        "files": norm_files(lab.get("files")),
        "main": lab["main"],
        "solution": norm_files(lab.get("solution")),
        "hints": [clean_md(h) for h in lab.get("hints", [])],
        "tests": norm_tests(lab.get("tests")),
    }
    if out["runtime"] not in RUNTIMES:
        raise ValueError(f"{ctx}: bad runtime {out['runtime']!r}")
    names = [f["name"] for f in out["files"]]
    if out["main"] not in names:
        raise ValueError(f"{ctx}: main {out['main']!r} not in files {names}")
    if not out["tests"]:
        raise ValueError(f"{ctx}: needs at least one test")
    sol_names = {f["name"] for f in out["solution"]}
    if not sol_names:
        raise ValueError(f"{ctx}: needs a solution")
    unknown = sol_names - set(names)
    if unknown:
        raise ValueError(f"{ctx}: solution has files not in starter: {sorted(unknown)}")
    return out


def norm_numeric(q, ctx):
    """One number, with a tolerance and a diagram.

    The tolerance is required rather than defaulted, because "how close is close
    enough" is a judgement about the physics that only the author can make: three
    significant figures on a reactance and two on a resistor colour code are both
    right, and a shared default would be wrong for one of them."""
    if not q:
        return None
    for key in ("title", "prompt"):
        if not q.get(key):
            raise ValueError(f"{ctx}/numeric: missing {key}")
    # `isinstance(True, int)` is True in Python, and `nan < 0` is False, so the
    # obvious spellings of these two checks both let nonsense through: a bool answer
    # and a NaN tolerance would each ship a question nobody can pass.
    def _num(x):
        return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)

    if not _num(q.get("answer")):
        raise ValueError(f"{ctx}/numeric: `answer` must be a finite number")
    if not _num(q.get("tol")) or q["tol"] < 0:
        raise ValueError(f"{ctx}/numeric: give an explicit finite, non-negative `tol`")
    if not q.get("why"):
        raise ValueError(f"{ctx}/numeric: no `why` \u2014 a correct answer still has to explain itself")
    dia = q.get("diagram")
    if dia is not None:
        if not (isinstance(dia, dict) and dia.get("parts")):
            raise ValueError(f"{ctx}/numeric: `diagram` must be a schematic with parts, or be left out")
        # The painter looks the kind up in PART_KINDS and dereferences the result, so
        # a typo does not draw a wrong symbol — it throws mid-paint and the question
        # renders as a blank panel with an error in the console.
        for i, p in enumerate(dia["parts"], 1):
            if p.get("kind") not in DIAGRAM_KINDS:
                raise ValueError(f"{ctx}/numeric/diagram part {i}: unknown kind "
                                 f"{p.get('kind')!r} (have: {', '.join(sorted(DIAGRAM_KINDS))})")
            for axis in ("x", "y"):
                if not isinstance(p.get(axis), int):
                    raise ValueError(f"{ctx}/numeric/diagram part {i}: {axis} must be an integer grid step")
    if dia is None and not q.get("figure"):
        raise ValueError(f"{ctx}/numeric: give a `diagram` or a `figure` \u2014 a bare number "
                         "with no picture is a quiz question, not this")
    given = q.get("given") or []
    for i, g in enumerate(given, 1):
        if not g.get("label") or g.get("value") in (None, ""):
            raise ValueError(f"{ctx}/numeric/given{i}: needs a label and a value")
    return {
        "title": q["title"],
        "minutes": int(q.get("minutes", 7)),
        "brief": clean_md(q.get("brief", "")),
        "prompt": clean_md(q["prompt"]),
        "note": clean_md(q.get("note", "")),
        "diagram": dia,
        "figure": clean_md(q.get("figure", "")),
        "given": [{"label": clean_md(g["label"]), "value": clean_md(str(g["value"]))} for g in given],
        "answer": float(q["answer"]),
        "tol": float(q["tol"]),
        "unit": q.get("unit", ""),
        "aside": clean_md(q.get("aside", "")),
        "hint": clean_md(q.get("hint", "")),
        "wrong": clean_md(q.get("wrong", "")),
        "why": clean_md(q["why"]),
    }


# the symbols src/circuit.js knows how to draw; build.mjs re-checks against the source
MATCH_SYMBOLS = {"R", "C", "L", "D", "LED", "GND", "V", "BATT", "I", "NPN", "PNP", "SW", "OPAMP"}

# what the schematic painter in src/circuit.js can put on a canvas. Narrower than the
# symbol list above on purpose: these are the kinds the SOLVER also understands, and a
# diagram is drawn by the solver's painter.
DIAGRAM_KINDS = {"R", "C", "L", "V", "I", "GND", "OUT"}


def norm_match(q, ctx):
    """Name the symbol. Recognition is its own skill and usually left to osmosis."""
    if not q:
        return None
    for key in ("title", "prompt"):
        if not q.get(key):
            raise ValueError(f"{ctx}/match: missing {key}")
    labels = q.get("labels") or []
    items = q.get("items") or []
    if len(set(labels)) != len(labels):
        dupe = [x for x in set(labels) if labels.count(x) > 1]
        raise ValueError(f"{ctx}/match: two labels read the same ({dupe!r}). The drill "
                         "accepts one specific index, so the learner can pick the "
                         "identical-looking wrong one and be marked wrong with no way "
                         "to tell why")
    if not 3 <= len(items) <= 8:
        raise ValueError(f"{ctx}/match: {len(items)} items (need 3-8)")
    if len(labels) < len(items):
        raise ValueError(f"{ctx}/match: {len(labels)} labels for {len(items)} items \u2014 "
                         "there must be at least one label per item")
    seen = set()
    out = []
    for i, it in enumerate(items, 1):
        where = f"{ctx}/match/{i}"
        sym = it.get("sym")
        if sym not in MATCH_SYMBOLS:
            raise ValueError(f"{where}: unknown symbol {sym!r} "
                             f"(have: {', '.join(sorted(MATCH_SYMBOLS))})")
        if sym in seen:
            raise ValueError(f"{where}: {sym!r} appears twice \u2014 two identical symbols "
                             "cannot be told apart, so one of them is unanswerable")
        seen.add(sym)
        a = it.get("a")
        if not isinstance(a, int) or not 0 <= a < len(labels):
            raise ValueError(f"{where}: `a` must index one of the labels")
        if not it.get("why"):
            raise ValueError(f"{where}: no `why`")
        out.append({"sym": sym, "a": a, "why": clean_md(it["why"])})
    if len({it["a"] for it in out}) != len(out):
        raise ValueError(f"{ctx}/match: two items share an answer label")
    return {
        "title": q["title"],
        "minutes": int(q.get("minutes", 6)),
        "brief": clean_md(q.get("brief", "")),
        "prompt": clean_md(q["prompt"]),
        "labels": [clean_md(x) for x in labels],
        "items": out,
    }


# the tunable models defined in src/studio.js, and the quantities each reports
TUNE_MODELS = {
    "divider": {"vout", "i", "ratio"},
    "rc-lowpass": {"fc", "keep", "reject", "tau"},
    "rlc": {"wn", "fn", "zeta", "peak"},
}


def norm_tune(q, ctx):
    """Move the sliders until every constraint holds at once.

    Constraints name a quantity the model reports, so a typo is caught here rather
    than becoming a target that can never be hit."""
    if not q:
        return None
    for key in ("title", "prompt", "model"):
        if not q.get(key):
            raise ValueError(f"{ctx}/tune: missing {key}")
    model = q["model"]
    if model not in TUNE_MODELS:
        raise ValueError(f"{ctx}/tune: unknown model {model!r} "
                         f"(have: {', '.join(sorted(TUNE_MODELS))})")
    keys = TUNE_MODELS[model]
    cons = q.get("constraints") or []
    if not cons:
        raise ValueError(f"{ctx}/tune: no constraints \u2014 that is a sandbox, not a target")
    out = []
    for i, c in enumerate(cons, 1):
        where = f"{ctx}/tune/constraint{i}"
        if c.get("k") not in keys:
            raise ValueError(f"{where}: {c.get('k')!r} is not reported by the {model!r} model "
                             f"(it reports: {', '.join(sorted(keys))})")
        if not c.get("label"):
            raise ValueError(f"{where}: needs a `label` the learner can read")
        bounds = [k for k in ("min", "max", "eq") if c.get(k) is not None]
        if not bounds:
            raise ValueError(f"{where}: give at least one of min, max or eq")
        if "eq" in bounds and c.get("tol") is None:
            raise ValueError(f"{where}: an `eq` constraint needs a `tol`")
        out.append({k: c[k] for k in ("k", "label", "min", "max", "eq", "tol") if c.get(k) is not None})
    return {
        "title": q["title"],
        "minutes": int(q.get("minutes", 9)),
        "brief": clean_md(q.get("brief", "")),
        "prompt": clean_md(q["prompt"]),
        "note": clean_md(q.get("note", "")),
        "model": model,
        "initial": q.get("initial", {}),
        "constants": q.get("constants", {}),
        "plotKey": q.get("plotKey", ""),
        "constraints": out,
    }


def norm_blanks(b, ctx):
    """A listing with holes in it, from the Voltaic design.

    The listing is authored with ___ where each blank goes; the nth ___ takes the nth
    entry of `blanks`. A blank works on an equation as readily as on code, which is
    how a physics module asks a question without pretending to be a programming one."""
    if not b:
        return None
    for key in ("title", "listing"):
        if not b.get(key):
            raise ValueError(f"{ctx}/blanks: missing {key}")
    holes = b["listing"].count("___")
    items = b.get("blanks") or []
    if holes != len(items):
        raise ValueError(f"{ctx}/blanks: the listing has {holes} ___ but "
                         f"{len(items)} blank(s) are defined")
    if not 2 <= len(items) <= 8:
        raise ValueError(f"{ctx}/blanks: {len(items)} blanks (need 2-8)")
    out = []
    for i, it in enumerate(items, 1):
        where = f"{ctx}/blanks/{i}"
        opts = it.get("opts") or []
        if not 2 <= len(opts) <= 5:
            raise ValueError(f"{where}: {len(opts)} options (need 2-5)")
        a = it.get("a")
        if not isinstance(a, int) or not 0 <= a < len(opts):
            raise ValueError(f"{where}: `a` must index one of the options")
        if not it.get("why"):
            raise ValueError(f"{where}: no `why` \u2014 the explanation is the teaching")
        no_positional_refs(it["why"], where)
        whys = it.get("whys")
        if whys is not None and len(whys) != len(opts):
            raise ValueError(f"{where}: `whys` must have one entry per option")
        out.append({
            "prompt": clean_md(it.get("prompt", "")),
            "hole": it.get("hole", ""),
            "opts": [clean_md(o) for o in opts],
            "a": a,
            "why": clean_md(it["why"]),
            "whys": [clean_md(w) for w in whys] if whys else None,
        })
    return {
        "title": b["title"],
        "minutes": int(b.get("minutes", 8)),
        "brief": clean_md(b.get("brief", "")),
        "caption": b.get("caption", ""),
        "lang": b.get("lang", "text"),
        "listing": clean_code(b["listing"]),
        "blanks": out,
    }


def norm_build(b, ctx):
    """A circuit the learner draws, graded by measuring it.

    Checks are JavaScript against the circuit API, so they express what the circuit
    must *do*. A check that compares the drawing to a reference would fail every
    correct alternative, which is the opposite of the point."""
    if not b:
        return None
    for key in ("title", "brief"):
        if not b.get(key):
            raise ValueError(f"{ctx}/build: missing {key}")
    checks = b.get("checks") or []
    if len(checks) < 3:
        raise ValueError(f"{ctx}/build: {len(checks)} checks (need at least 3)")
    # A reference schematic is required for the same reason a lab needs a reference
    # solution: without one there is no way to prove the checks can be passed at all.
    sol = b.get("solution")
    if not sol or not sol.get("parts"):
        raise ValueError(f"{ctx}/build: no `solution` schematic — the gate cannot "
                         "prove the checks are satisfiable without one")
    out = []
    for i, c in enumerate(checks, 1):
        if not c.get("name") or not c.get("code"):
            raise ValueError(f"{ctx}/build/check{i}: needs a name and code")
        out.append({"name": c["name"], "code": clean_md(c["code"])})
    return {
        "title": b["title"],
        "minutes": int(b.get("minutes", 20)),
        "brief": clean_md(b["brief"]),
        "start": b.get("start") or {"parts": [], "wires": []},
        "solution": sol,
        "checks": out,
        "hints": [clean_md(h) for h in b.get("hints", [])],
    }


def norm_quiz(q, ctx):
    """Short questions with an explanation on every option.

    A foundational course needs somewhere to check that a definition landed before
    asking anyone to derive with it. The `why` is required on every question because
    a quiz that only says "wrong" teaches nothing; it is shown whichever option was
    picked."""
    if not q:
        return None
    if not q.get("title"):
        raise ValueError(f"{ctx}/quiz: missing title")
    qs = q.get("questions") or []
    if not 3 <= len(qs) <= 10:
        raise ValueError(f"{ctx}/quiz: {len(qs)} questions (need 3-10)")
    out = []
    for i, item in enumerate(qs, 1):
        where = f"{ctx}/quiz/q{i}"
        if not item.get("q"):
            raise ValueError(f"{where}: no question text")
        opts = item.get("opts") or []
        if len(opts) != 4:
            raise ValueError(f"{where}: {len(opts)} options (need exactly 4 \u2014 the "
                             "answer key is labelled A-D)")
        a = item.get("a")
        if not isinstance(a, int) or not 0 <= a < 4:
            raise ValueError(f"{where}: `a` must be the index 0-3 of the correct option")
        if not item.get("why"):
            raise ValueError(f"{where}: no `why` \u2014 an explanation is the point of asking")
        no_positional_refs(item["why"], where)
        out.append({
            "q": clean_md(item["q"]),
            "opts": [clean_md(o) for o in opts],
            "a": a,
            "why": clean_md(item["why"]),
        })
    return {"title": q["title"], "minutes": int(q.get("minutes", 6)), "questions": out}


def norm_sandbox(sb, ctx):
    """The intuition step: a visualiser id and the parameters it opens with.

    Nothing is graded here, so validation is only about not shipping a unit that
    points at a visualiser the build does not contain."""
    if not sb:
        return None
    for key in ("title", "visualiser"):
        if not sb.get(key):
            raise ValueError(f"{ctx}/sandbox: missing {key}")
    notice = [clean_md(n) for n in sb.get("notice", [])]
    if len(notice) < 2:
        raise ValueError(f"{ctx}/sandbox: give at least 2 things to notice, "
                         "or the learner has nothing to look for")
    return {
        "title": sb["title"],
        "visualiser": sb["visualiser"],
        "minutes": int(sb.get("minutes", 8)),
        "brief": clean_md(sb.get("brief", "")),
        "initial": sb.get("initial", {}),
        "notice": notice,
    }


POSITIONAL = re.compile(
    r"\b(?:[Oo]ption|[Cc]hoice|[Aa]nswer)s?\s+[A-E]\b"
    r"|\b[Tt]he\s+(?:first|second|third|fourth|fifth|last|final)"
    r"\s+(?:option|choice|answer)\b",
)  # case-sensitive on purpose: "answers a question" is ordinary prose, not a pointer


def no_positional_refs(text, where):
    """Options are shuffled per learner, so "Option D" names nothing.

    The shuffle exists because the generated quizzes park the answer in one slot far
    too often — 61% of one course's answers sat in B. Prose that points at a position
    was written before the shuffle and stopped being true the day it landed, so it is
    rejected here rather than left to rot. Name the option by what it says."""
    hit = POSITIONAL.search(text or "")
    if hit:
        raise ValueError(
            f"{where}: the explanation says {hit.group(0)!r}, but the options are "
            "shuffled per learner — name the option by its content instead"
        )


LEAKED = []  # derivation steps whose placeholder was the answer


def norm_derive(dv, ctx):
    """The guided derivation. Every step is checked symbolically, so every step
    needs an answer; a step with no way forward when stuck is a dead end, so a
    hint or a deconstruction is required too."""
    if not dv:
        return None
    if not dv.get("title"):
        raise ValueError(f"{ctx}/derive: missing title")
    steps = dv.get("steps") or []
    if not 2 <= len(steps) <= 8:
        raise ValueError(f"{ctx}/derive: {len(steps)} steps (need 2-8)")
    out_steps = []
    for i, st in enumerate(steps, 1):
        where = f"{ctx}/derive/step{i}"
        if not st.get("prompt"):
            raise ValueError(f"{where}: no prompt")
        if not st.get("answer"):
            raise ValueError(f"{where}: no answer to check against")
        if not st.get("hint") and not st.get("deconstruct"):
            raise ValueError(f"{where}: needs a hint or a deconstruction, "
                             "otherwise a stuck learner has nowhere to go")
        # A placeholder is a hint about the *shape* of the answer. Set equal to the
        # answer it is not a hint, it is the answer, printed in the box the learner
        # is supposed to fill. That is how the first course was written and how every
        # course after it was written, so it is dropped here rather than in 337 places.
        ph = st.get("placeholder", "")
        if "".join(ph.split()) == "".join(st["answer"].split()):
            LEAKED.append(where)
            ph = ""
        out_steps.append({
            "prompt": clean_md(st["prompt"]),
            "given": clean_md(st.get("given", "")),
            "answer": st["answer"].strip(),
            "placeholder": ph,
            "hint": clean_md(st.get("hint", "")),
            "deconstruct": [clean_md(d) for d in st.get("deconstruct", [])],
        })
    if not dv.get("vars"):
        raise ValueError(f"{ctx}/derive: list the symbols in `vars`, or multi-letter "
                         "names like V_out are split into single symbols")
    return {
        "title": dv["title"],
        "minutes": int(dv.get("minutes", 12)),
        "brief": clean_md(dv.get("brief", "")),
        "vars": list(dv["vars"]),
        "steps": out_steps,
        "closing": clean_md(dv.get("closing", "")),
    }


def normalise(course):
    cid = course["id"]
    # `band` is the current name; `year` is still accepted from older modules
    if "band" in course and "year" not in course:
        course["year"] = course["band"]
    for key in ("id", "title", "year", "level", "summary", "modules", "capstone"):
        if key not in course:
            raise ValueError(f"{cid}: missing {key!r}")
    if course["level"] not in LEVELS:
        raise ValueError(f"{cid}: bad level {course['level']!r}")

    mods = []
    for i, m in enumerate(course["modules"], 1):
        ctx = f"{cid}/M{i}"
        if not m.get("concepts"):
            raise ValueError(f"{ctx}: no concepts")
        mods.append({
            "title": m["title"],
            "summary": clean_md(m.get("summary", "")),
            "concepts": [clean_md(c) for c in m["concepts"]],
            "sandbox": norm_sandbox(m.get("sandbox"), ctx),
            "quiz": norm_quiz(m.get("quiz"), ctx),
            "blanks": norm_blanks(m.get("blanks"), ctx),
            "numeric": norm_numeric(m.get("numeric"), ctx),
            "match": norm_match(m.get("match"), ctx),
            "tune": norm_tune(m.get("tune"), ctx),
            "build": norm_build(m.get("build"), ctx),
            "derive": norm_derive(m.get("derive"), ctx),
            "lab": norm_lab(m.get("lab"), ctx),
        })
    if not 3 <= len(mods) <= 5:
        raise ValueError(f"{cid}: {len(mods)} modules (need 3-5)")

    cap = course["capstone"]
    capstone = {
        "title": cap["title"],
        "brief": clean_md(cap["brief"]),
        "deliverables": [clean_md(d) for d in cap.get("deliverables", [])],
        "constraints": [clean_md(c) for c in cap.get("constraints", [])],
        "rubric": [{"criterion": r["criterion"], "weight": int(r["weight"]),
                    "evidence": clean_md(r["evidence"])} for r in cap.get("rubric", [])],
        "runtime": cap.get("runtime", "python"),
        "minutes": int(cap.get("minutes", 240)),
        "files": norm_files(cap.get("files")),
        "main": cap.get("main"),
        "solution": norm_files(cap.get("solution")),
        "hints": [clean_md(h) for h in cap.get("hints", [])],
        "tests": norm_tests(cap.get("tests")),
    }
    if len(capstone["deliverables"]) < 3:
        raise ValueError(f"{cid}: capstone has {len(capstone['deliverables'])} "
                         "deliverable(s), need at least 3")
    if not 3 <= len(capstone["rubric"]) <= 5:
        raise ValueError(f"{cid}: capstone rubric has {len(capstone['rubric'])} "
                         "criteria, need 3-5")
    for r in capstone["rubric"]:
        if len(r["criterion"]) < 4 or len(r["evidence"]) < 20:
            raise ValueError(f"{cid}: rubric row {r['criterion']!r} is a placeholder — "
                             "give it a real criterion and a sentence of evidence")
    total = sum(r["weight"] for r in capstone["rubric"])
    if total != 100:
        raise ValueError(f"{cid}: rubric weights sum to {total}, need 100")
    if len(capstone["tests"]) < 4:
        raise ValueError(f"{cid}: capstone has {len(capstone['tests'])} checks, "
                         "need at least 4 — the capstone must be runnable")
    norm_lab({**capstone, "title": capstone["title"]}, f"{cid}/CAP")

    return {
        "id": cid,
        "title": course["title"],
        "year": int(course["year"]),
        "level": course["level"],
        "prereqs": list(course.get("prereqs", [])),
        "stack": list(course.get("stack", [])),
        "credits": int(course.get("credits", 10)),
        "hours": int(course.get("hours", 120)),
        "icon": course.get("icon", "◆"),
        "summary": clean_md(course["summary"]),
        "outcomes": [clean_md(o) for o in course.get("outcomes", [])],
        "assessment": clean_md(course.get("assessment", "")),
        "reading": [clean_md(r) for r in course.get("reading", [])],
        "modules": mods,
        "capstone": capstone,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    paths = args.paths
    if args.all or not paths:
        paths = sorted(glob.glob(os.path.join(AUTHORS, "*.py")))
    if not paths:
        print("no author modules found in", AUTHORS)
        return 1

    failures = 0
    for path in paths:
        try:
            mod = load_module(path)
            course = normalise(mod.COURSE)
        except Exception as e:
            print(f"[FAIL] {os.path.basename(path)}: {type(e).__name__}: {e}")
            failures += 1
            continue
        dest = os.path.join(OUT, course["id"] + ".json")
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump(course, fh, indent=1, ensure_ascii=False)
        labs = sum(1 for m in course["modules"] if m["lab"])
        print(f"[ ok ] {course['id']:<8} {len(course['modules'])} modules, "
              f"{labs} labs, capstone "
              f"{'+tests' if course['capstone']['tests'] else '(spec only)'}"
              f" -> {os.path.relpath(dest, ROOT)}")

    if LEAKED:
        print("")
        print(f"{len(LEAKED)} derivation step(s) had the answer as the placeholder; "
              "dropped. Write a shape hint instead, or leave it out:")
        for w in LEAKED[:8]:
            print("   ", w)
        if len(LEAKED) > 8:
            print(f"    ... and {len(LEAKED) - 8} more")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
