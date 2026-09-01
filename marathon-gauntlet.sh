#!/usr/bin/env bash
#
# Codex Learn — adversarial gauntlet runner.
#
#   ./marathon-gauntlet.sh [hours]        default 3
#
# Rotates through the six tracks, one headless Claude Code cycle each, and commits
# after any cycle whose gates come out clean.
#
# NOT `set -e`. The loop has to outlive a failing cycle: a usage limit, a network
# blip or one bad patch should cost that cycle and nothing else. Failures are caught
# and reported per cycle instead.

DURATION_HOURS="${1:-3}"
END_TIME=$(( $(date +%s) + DURATION_HOURS * 3600 ))
LOG=GAUNTLET_LOG.md

TRACKS=(
  "TRACK 1: Content & Conceptual Depth (deepen explanations, derive rather than announce, worked examples end to end)"
  "TRACK 2: Interactive Models & Visualizers (sandboxes, tune models, the circuit editor: extremes, resize, rapid input)"
  "TRACK 3: Question Bank & Quizzes (misconception-driven distractors, feedback that explains the wrong answer too)"
  "TRACK 4: Subject Breadth (missing topics, prerequisite bridges, novice-to-advanced progression)"
  "TRACK 5: UI, Layout & Visual Aesthetics (typography, both themes, mobile, micro-interactions)"
  "TRACK 6: Edge Cases, Resilience & Accessibility (keyboard, ARIA, focus, persistence, zero console errors)"
)

if [ ! -f "$LOG" ]; then
  { echo "# Codex Learn — Gauntlet Execution Log"; echo; echo "Started $(date '+%Y-%m-%d %H:%M')"; echo; } > "$LOG"
fi

# `date -r <epoch>` is BSD. GNU date reads -r as a FILENAME and errors, which is what
# happens on this machine, so format the end time the portable way.
end_human=$(date -d "@$END_TIME" '+%H:%M:%S' 2>/dev/null || date '+%H:%M:%S')

echo "=========================================================="
echo "Codex Learn adversarial gauntlet"
echo "Duration: ${DURATION_HOURS}h   ends about ${end_human}"
echo "=========================================================="

# Gates that are cheap enough to run every cycle. build.mjs last: it is the one that
# refuses a catalog older than its source, and it writes the artifacts.
run_gates() {
  local ok=0
  node tools/verify_circuits.mjs   >/tmp/g_circ.txt 2>&1 || ok=1
  node tools/verify_tune.mjs       >/tmp/g_tune.txt 2>&1 || ok=1
  node tools/verify_numeric.mjs    >/tmp/g_num.txt  2>&1 || ok=1
  python -X utf8 tools/verify_derivations.py >/tmp/g_der.txt 2>&1 || ok=1
  node build.mjs                   >/tmp/g_build.txt 2>&1 || ok=1
  return $ok
}

# A headless cycle that cannot write the repo or run node still exits 0, still
# prints a thoughtful audit, and changes nothing. Six cycles did exactly that before
# anyone noticed, and the only durable trace was a memory file. So prove the loop can
# act before spending three hours finding out it cannot.
echo "preflight: can a headless cycle write and execute?"
rm -f .gauntlet-probe
claude -p --permission-mode acceptEdits \
  "You are the preflight check for this repository's automated improvement pipeline, which is about to run unattended for several hours. Its cycles edit source files and run the verification gates. A cycle that cannot do those exits successfully having changed nothing, which is indistinguishable from one that worked - six did exactly that before this check existed. So confirm the pipeline can act: write the single word ok into a file called .gauntlet-probe in the current directory, then run node -e \"console.log(1+1)\". Then reply with the word ready and nothing else." \
  >/tmp/g_probe.txt 2>&1
if [ ! -f .gauntlet-probe ]; then
  echo
  echo "ABORT: the cycle did not write .gauntlet-probe."
  if grep -qiE "permission|denied|not allowed" /tmp/g_probe.txt; then
    echo "It was DENIED. Check .claude/settings.local.json."
  else
    echo "It was not denied - it declined. A probe that reads as a pointless"
    echo "capability test gets asked what you actually want. Its reply is below."
  fi
  echo "A headless run without permission to write and execute audits into its own"
  echo "scratchpad and exits 0, so the loop would look healthy and produce nothing."
  echo "Check .claude/settings.local.json, or pass --dangerously-skip-permissions."
  echo
  tail -20 /tmp/g_probe.txt
  exit 1
fi
rm -f .gauntlet-probe
echo "preflight: ok"
echo

CYCLE=1
CONSEC_FAIL=0

while [ "$(date +%s)" -lt "$END_TIME" ]; do
  TRACK="${TRACKS[$(( (CYCLE - 1) % ${#TRACKS[@]} ))]}"
  REMAINING=$(( (END_TIME - $(date +%s)) / 60 ))

  echo
  echo "----------------------------------------------------------"
  echo "Cycle $CYCLE  |  $TRACK"
  echo "~${REMAINING} min remaining"
  echo "----------------------------------------------------------"

  started=$(date +%s)
  claude -p --permission-mode acceptEdits "Read GAUNTLET_CURRICULUM.md and GAUNTLET_LOG.md. Execute cycle $CYCLE, focused strictly on: $TRACK.

Pick ONE course or ONE subsystem — a cycle that touches everything verifies nothing.
Capture the gate baseline BEFORE editing. Audit through all four personas and write
the attacks into the log, including anything you decided to leave alone and why.
Apply substantial improvements. Then run every gate that touches this track and
confirm the pre-existing numbers have not moved. Append your summary to
GAUNTLET_LOG.md."
  rc=$?
  elapsed=$(( $(date +%s) - started ))

  if [ $rc -ne 0 ]; then
    echo "!! cycle $CYCLE exited $rc after ${elapsed}s"
    CONSEC_FAIL=$(( CONSEC_FAIL + 1 ))
  elif [ $elapsed -lt 45 ]; then
    # A cycle that returns 0 in seconds did no work — usually a usage limit reported
    # on stdout. Spinning through six tracks a minute would fill the log with nothing.
    echo "!! cycle $CYCLE returned in ${elapsed}s — treating as a no-op"
    CONSEC_FAIL=$(( CONSEC_FAIL + 1 ))
  else
    CONSEC_FAIL=0
  fi

  # Back off hard rather than hammering a limit that resets in hours.
  if [ $CONSEC_FAIL -ge 3 ]; then
    echo "!! three unproductive cycles in a row — sleeping 30 min"
    sleep 1800
    CONSEC_FAIL=0
  fi

  # Commit only what passes. Committing unverified content is how a broken catalog
  # becomes the baseline for the next cycle.
  if [ -d .git ]; then
    if [ -n "$(git status --porcelain)" ]; then
      if run_gates; then
        git add -A
        git commit -q -m "gauntlet: cycle $CYCLE — ${TRACK%% (*}" && echo "committed cycle $CYCLE"
      else
        echo "!! GATES FAILED — not committing cycle $CYCLE. See /tmp/g_*.txt"
        {
          echo
          echo "## Cycle $CYCLE — GATES FAILED, not committed"
          echo '```'
          tail -3 /tmp/g_circ.txt /tmp/g_tune.txt /tmp/g_num.txt /tmp/g_der.txt /tmp/g_build.txt 2>/dev/null
          echo '```'
        } >> "$LOG"
      fi
    else
      echo "no changes this cycle — counting it as unproductive"
      CONSEC_FAIL=$(( CONSEC_FAIL + 1 ))
    fi
  fi

  CYCLE=$(( CYCLE + 1 ))
  sleep 3
done

echo
echo "=========================================================="
echo "Gauntlet finished after $(( CYCLE - 1 )) cycles."
echo "Read $LOG and 'git log' for what happened."
echo "=========================================================="
