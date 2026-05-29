#!/usr/bin/env bash
# MAIN-TRACK gate A1: powered decoy ablation. Run the full ladder on the HOT
# 14B cells (synonym=7.2%, matched_random) at n=100 so C0 fires ~15-25 events
# -> the C0.7/C0.8/C1 "content is decorative" equivalence becomes a POWERED
# test instead of three zeros. Chains after run_lean.sh (no GPU contention).
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] PWR $*" | tee -a "$QDIR/powered.log"; }
log "waiting for run_lean.sh to drain…"
while pgrep -f "run_lean.sh" >/dev/null 2>&1; do sleep 300; done
log "lean drained — starting powered decoy ablation on hot 14B cells."
for C in C0 C0_7 C0_8 C1; do
  marker="$QDIR/.done_pwr_14B_${C}"; [[ -f "$marker" ]] && { log "SKIP 14B $C"; continue; }
  rid="qwen3_14B_${C}_pwr_$(date +%s)"; log "START 14B $C n=100 (synonym,matched_random) -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models mlx-community/Qwen3-14B-4bit \
    --distractor-types synonym,matched_random --n 100 --condition "$C" --remove-target \
    --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$marker"
  log "DONE 14B $C | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log" | tail -2 | tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1
done
log "===== POWERED DECOY ABLATION COMPLETE ====="
