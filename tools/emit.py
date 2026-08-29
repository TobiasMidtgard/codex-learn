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


def normalise(course):
    cid = course["id"]
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
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
