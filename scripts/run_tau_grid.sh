#!/usr/bin/env bash
# 2nd-benchmark (tau-bench) TFR grid -> SEPARATE output dir (results_tau) so the
# global BFCL aggregator never pools it. Does the open-vs-closed gap reproduce
# on a genuinely different benchmark? API agents run now; Qwen3 (M5) chains after mt2.
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; OUT="results_tau"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
set -a; [ -f "$ROOT/.env.local" ] && . "$ROOT/.env.local"; set +a
log(){ echo "[$(date '+%H:%M:%S')] TAU $*" | tee -a "$QDIR/tau.log"; }
cell(){ local model="$1"; local short; short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-4bit//')
  local mk="$QDIR/.done_tau_${short}"; [[ -f "$mk" ]] && { log "SKIP $short"; return; }
  local rid="tau_${short}_C0_$(date +%s)"; log "START $short (tau-bench) -> $OUT/$rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" --benchmark tau_bench \
    --distractor-types near_name,synonym,matched_random,unrelated --n 25 --condition C0 \
    --remove-target --output "$OUT" --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"; }
log "===== TAU GRID START (commercial via API, now) ====="
for M in claude-haiku-4-5 claude-sonnet-4-6 gpt-4.1; do cell "$M"; done
log "commercial side done — waiting for run_mt2.sh to free the M5 for Qwen3…"
while pgrep -f "run_mt2.sh" >/dev/null 2>&1; do sleep 300; done
log "M5 free — running open-weight side (the gap test)."
for M in mlx-community/Qwen3-8B-4bit mlx-community/Qwen3-14B-4bit; do cell "$M"; done
log "===== TAU GRID COMPLETE ====="
