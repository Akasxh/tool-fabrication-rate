#!/usr/bin/env bash
# Prioritized main-track compute (value order):
#  1) POWERED DECOY ABLATION (the #1 panel fix) — 14B hot cell, n=100, events under the ladder
#  2) bf16 quant control (#2 fix) — de-confound scale vs 4-bit
#  3) A2 reflection comparator (re-run)
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] MT $*" | tee -a "$QDIR/mt.log"; }
cell(){ # model cond n  distractors
  local model="$1" cond="$2" n="$3" dist="$4"
  local short; short=$(echo "$model"|sed 's#.*/##;s/Qwen3-//;s/-4bit//')
  local mk="$QDIR/.done_mt_${short}_${cond}_${n}"; [[ -f "$mk" ]] && { log "SKIP $short $cond"; return; }
  local rid="qwen3_${short}_${cond}_mt_$(date +%s)"; log "START $short $cond n=$n [$dist] -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" --distractor-types "$dist" \
    --n "$n" --condition "$cond" --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"
  log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -2|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1
}
log "===== PRIORITIZED MAIN-TRACK QUEUE START ====="
# 1) powered decoy ablation on hot 14B cell — C0 establishes events, then the three interventions
for C in C0 C1 C0_8 C0_7; do cell mlx-community/Qwen3-14B-4bit "$C" 100 "synonym,matched_random"; done
# 2) bf16 quant control
cell mlx-community/Qwen3-8B-bf16  C0 25 "near_name,synonym,matched_random,unrelated"
cell mlx-community/Qwen3-14B-8bit C0 25 "near_name,synonym,matched_random,unrelated"
# 3) A2 reflection comparator
cell mlx-community/Qwen3-8B-4bit  A2 25 "near_name,synonym,matched_random,unrelated"
log "===== PRIORITIZED QUEUE COMPLETE ====="
