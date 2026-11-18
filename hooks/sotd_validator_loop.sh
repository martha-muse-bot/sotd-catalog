#!/usr/bin/env bash
# Detector for the SOTD catalog validator continuous loop.
# Wakes a worker as soon as the previous batch's finish marker postdates
# its wake; the ~25-minute last-wake gate remains only as a watchdog for
# crashed or very long batches. Disables itself when the queue drains.
#
# Two-queue design (2026-10-30): the primary queue is the workers'
# worklist. Items blocked on parent-only work (browser checks, decisions)
# escalate to state 'awaiting_parent' — the escalation queue. Workers take
# only 'pending' via next_queue, so they never stall behind the escalation
# queue. The drain check counts both states; the wake logic only counts
# actionable pending items.
set -euo pipefail
source "$HATCH_HOOK_RUNTIME"

DB="$HOME/workspace/sotd/catalog/catalog.db"
LOCK="$HOME/workspace/sotd/catalog/.catalog.lock"
STATE_DIR="$HOME/hooks/state/sotd_validator_loop"
LAST="$STATE_DIR/last_wake"
FINISH="$STATE_DIR/last_finish"
mkdir -p "$STATE_DIR"

counts=$(python3 -c "
import sqlite3
c = sqlite3.connect('file:$DB?mode=ro', uri=True)
st = dict(c.execute('SELECT state, COUNT(*) FROM queue GROUP BY state'))
print(st.get('pending', 0), st.get('awaiting_parent', 0))
")
actionable=$(echo "$counts" | cut -d' ' -f1)
awaiting=$(echo "$counts" | cut -d' ' -f2)

if [ "$actionable" -eq 0 ] && [ "$awaiting" -eq 0 ]; then
  disable_after_run
  silent "validation queue drained" '{"pending":0,"awaiting_parent":0}'
fi

if [ "$actionable" -eq 0 ]; then
  silent "only escalation-queue items remain" "{\"pending\":0,\"awaiting_parent\":$awaiting}"
fi
pending=$actionable

if [ -f "$LOCK" ]; then
  lock_age=$(( $(date +%s) - $(stat -c %Y "$LOCK") ))
  if [ "$lock_age" -lt 7200 ]; then
    silent "catalog lock held by another pass" "{\"pending\":$pending,\"lock_age_s\":$lock_age}"
  fi
fi

if [ -f "$LAST" ]; then
  age=$(( $(date +%s) - $(cat "$LAST") ))
  finished=0
  if [ -f "$FINISH" ]; then
    finish_ts=$(cat "$FINISH")
    case "$finish_ts" in
      ''|*[!0-9]*) ;;
      *)
        if [ "$finish_ts" -gt "$(cat "$LAST")" ]; then
          finished=1
        fi
        ;;
    esac
  fi
  if [ "$finished" -eq 0 ] && [ "$age" -lt 1500 ]; then
    silent "validator worker woken recently" "{\"pending\":$pending,\"last_wake_age_s\":$age}"
  fi
fi

if [ "${HATCH_HOOK_DRY_RUN:-0}" != "1" ]; then
  date +%s > "$LAST"
fi
wake "sotd validation items pending" "{\"pending\":$pending,\"awaiting_parent\":$awaiting}"
