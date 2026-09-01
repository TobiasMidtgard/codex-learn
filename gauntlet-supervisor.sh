#!/usr/bin/env bash
#
# Keeps the gauntlet running, unattended, until a deadline.
#
#   ./gauntlet-supervisor.sh [total-hours] [per-run-hours]     default 12 3
#
# marathon-gauntlet.sh stops when its own clock runs out, which then needs someone to
# notice and relaunch it. This waits for whatever run is in flight, starts the next
# one, and keeps doing that until the total is spent — so an overnight run needs no
# one watching it.
#
# Never starts a second gauntlet alongside a first: two of them would edit the same
# files from different cycles and the gates would blame whichever finished last.

TOTAL_HOURS="${1:-12}"
RUN_HOURS="${2:-3}"
DEADLINE=$(( $(date +%s) + TOTAL_HOURS * 3600 ))
LOG=gauntlet-supervisor.log

running() {
  # The runner is a bash process whose command line names the script. On Git Bash,
  # `ps` does not show it reliably, so ask Windows.
  wmic process where "name='bash.exe'" get CommandLine 2>/dev/null |
    grep -qi "marathon-gauntlet"
}

say() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }

say "supervisor up: ${TOTAL_HOURS}h total, ${RUN_HOURS}h per run"

if running; then
  say "a gauntlet is already running — waiting for it rather than starting a second"
  while running && [ "$(date +%s)" -lt "$DEADLINE" ]; do sleep 60; done
  say "that run finished"
fi

RUN=1
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  left_h=$(( (DEADLINE - $(date +%s)) / 3600 ))
  # Do not start a 3-hour run with 20 minutes left on the clock.
  this_run=$RUN_HOURS
  [ "$left_h" -lt "$RUN_HOURS" ] && this_run=$(( left_h > 0 ? left_h : 1 ))
  if [ $(( DEADLINE - $(date +%s) )) -lt 1200 ]; then
    say "under 20 min left — stopping rather than starting a run that cannot finish"
    break
  fi

  say "starting run $RUN (${this_run}h)"
  ./marathon-gauntlet.sh "$this_run" >> gauntlet.out 2>&1
  rc=$?
  say "run $RUN exited $rc"

  # The runner aborts on a failed preflight, which is a configuration problem no
  # amount of retrying fixes. Anything else — a usage limit, a crash — is worth
  # another go after a pause.
  if [ $rc -eq 1 ] && tail -20 gauntlet.out | grep -q "ABORT: the cycle could not write"; then
    say "preflight failed: the cycles cannot write. Fix permissions; not retrying."
    break
  fi

  RUN=$(( RUN + 1 ))
  sleep 30
done

say "supervisor done after $(( RUN - 1 )) run(s)"
