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
