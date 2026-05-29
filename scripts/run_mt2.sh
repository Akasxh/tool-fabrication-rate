#!/usr/bin/env bash
# Reprioritized M5 queue (positioning-research-driven): the powered decoy is
# DEPRIORITIZED (it upgrades a demoted supporting claim). Focus on what supports
# the commercial-vs-open headline + breadth:
#   1) bf16 quant control (is the open-weight gap a 4-bit artifact?)
#   2) cross-family breadth (2nd/3rd open family: Llama, Mistral, Qwen2.5 + RVR)
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] MT2 $*" | tee -a "$QDIR/mt2.log"; }
cell(){ local model="$1" cond="$2" n="$3"; local short; short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-4bit//')
  local mk="$QDIR/.done_mt2_${short}_${cond}"; [[ -f "$mk" ]] && { log "SKIP $short $cond"; return; }
  local rid="mt2_${short}_${cond}_$(date +%s)"; log "START $short $cond n=$n -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated --n "$n" --condition "$cond" \
    --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1; }
log "===== REPRIORITIZED QUEUE START ====="
# 1) bf16 quant control (de-confound the headline gap)
cell mlx-community/Qwen3-8B-bf16  C0 25
cell mlx-community/Qwen3-14B-8bit C0 25
# 2) cross-family breadth + RVR generalization
for M in mlx-community/Llama-3.1-8B-Instruct-4bit mlx-community/Mistral-7B-Instruct-v0.3-4bit; do
  cell "$M" C0 20; cell "$M" C1 20; done
cell mlx-community/Qwen2.5-7B-Instruct-4bit C1 20
log "===== REPRIORITIZED QUEUE COMPLETE ====="
