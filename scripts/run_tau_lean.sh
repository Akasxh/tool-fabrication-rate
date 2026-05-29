#!/usr/bin/env bash
set +e; cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] TAULEAN $*" | tee -a "$QDIR/tau_lean.log"; }
log "waiting for run_final2 (fast quant+cross-family) to finish first…"
while pgrep -f "run_final2.sh" >/dev/null 2>&1; do sleep 200; done
log "fast experiments done — running LEAN tau gap test (high-yield arms, n=12)."
for M in mlx-community/Qwen3-8B-4bit mlx-community/Qwen3-14B-4bit; do
  short=$(echo "$M"|sed 's#.*/##;s/-4bit//'); mk="$QDIR/.done_taulean_${short}"; [[ -f "$mk" ]] && { log "SKIP $short"; continue; }
  rid="taulean_${short}_$(date +%s)"; log "START $short tau-gap (synonym,matched_random n=12)"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$M" --benchmark tau_bench \
    --distractor-types synonym,matched_random --n 12 --condition C0 --remove-target \
    --output results_tau --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -2|tr '\n' ' ')"
done
log "===== LEAN TAU GAP COMPLETE ====="
