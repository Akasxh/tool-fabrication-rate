#!/usr/bin/env bash
# Baseline-completeness ladder (chains after queue2). Adds the Reflexion-style
# ungrounded-reflection arm (A2) + naive-retry (C0.5) at n=100 on the 8B
# ablation tier, so the full ladder C0 / C0.5 / A2 / C0.7 / C0.8 / C1 is
# comparable at matched n and rebuts "is RVR just reflection/retry?".
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] Q3 $*" | tee -a "$QDIR/queue3.log"; }
log "waiting for run_queue2.sh to drain…"
while pgrep -f "run_queue2.sh" >/dev/null 2>&1; do sleep 300; done
log "queue2 drained — starting baseline-completeness ladder."
for C in A2 C0_5; do
  marker="$QDIR/.done_q3_8B_${C}"; [[ -f "$marker" ]] && { log "SKIP 8B $C"; continue; }
  rid="qwen3_8B_${C}_q3_$(date +%s)"; log "START 8B $C n=100 -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models mlx-community/Qwen3-8B-4bit \
    --distractor-types near_name,synonym,matched_random,unrelated \
    --n 100 --condition "$C" --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$marker"
  log "DONE 8B $C | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log" | tail -4 | tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1
done
log "===== BASELINE LADDER COMPLETE ====="
