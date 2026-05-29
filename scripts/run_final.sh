#!/usr/bin/env bash
set +e; cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] FINAL $*" | tee -a "$QDIR/final.log"; }
log "waiting for tau grid (Qwen3 gap test) to finish first…"
while pgrep -f "run_tau_grid.sh" >/dev/null 2>&1; do sleep 200; done
log "tau gap test done — running quant control (8-bit, fits) + cross-family."
cell(){ local model="$1" cond="$2" n="$3"; local short; short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-4bit//')
  local mk="$QDIR/.done_final_${short}_${cond}"; [[ -f "$mk" ]] && { log "SKIP $short $cond"; return; }
  local rid="final_${short}_${cond}_$(date +%s)"; log "START $short $cond"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated --n "$n" --condition "$cond" \
    --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1; }
cell mlx-community/Qwen3-8B-8bit  C0 25      # quant control (4bit vs 8bit), fits at 8.7GB
cell mlx-community/Qwen3-14B-8bit C0 25      # 15.7GB, fits
for M in mlx-community/Llama-3.1-8B-Instruct-4bit mlx-community/Mistral-7B-Instruct-v0.3-4bit; do
  cell "$M" C0 20; cell "$M" C1 20; done
cell mlx-community/Qwen2.5-7B-Instruct-4bit C1 20
log "===== FINAL QUEUE COMPLETE ====="
