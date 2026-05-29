#!/usr/bin/env bash
# Main-track BREADTH gate (chains after run_mt.sh): a 2nd/3rd open-weight family
# + RVR generalization beyond Qwen3. Cross-family parser fix is already merged.
#   - Llama-3.1-8B, Mistral-7B-v0.3: C0 (do they fabricate?) + C1 (does RVR fix it?)
#   - Qwen2.5-7B: C1 (RVR on the lineage's 6.10% baseline)
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] BRD $*" | tee -a "$QDIR/breadth.log"; }
log "waiting for run_mt.sh to drain…"; while pgrep -f "run_mt.sh" >/dev/null 2>&1; do sleep 300; done
log "MT drained — starting cross-family breadth."
cell(){ local model="$1" cond="$2"; local short; short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-4bit//')
  local mk="$QDIR/.done_brd_${short}_${cond}"; [[ -f "$mk" ]] && { log "SKIP $short $cond"; return; }
  local rid="brd_${short}_${cond}_$(date +%s)"; log "START $short $cond -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated --n 20 --condition "$cond" \
    --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1; }
for M in mlx-community/Llama-3.1-8B-Instruct-4bit mlx-community/Mistral-7B-Instruct-v0.3-4bit; do
  cell "$M" C0; cell "$M" C1; done
cell mlx-community/Qwen2.5-7B-Instruct-4bit C1
log "===== BREADTH COMPLETE ====="
