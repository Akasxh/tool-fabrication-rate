#!/usr/bin/env bash
# Overnight session 2:
#  P1 - POWERED content-vs-format ablation on Qwen2.5-7B (C0 base = 6.10%, ~4x Qwen3-8B).
#       C0_8 (decoy/WRONG list) is the key content test; C0_7 (no list) and C0_5 (naive
#       retry) complete the ladder. High N -> powers the §6 mechanism claim that was only
#       bounded (+/-1.5pp) on the low-base-rate Qwen3-8B ablation.
#  P2 - Gemma-2-9B (Google lineage, 4th family) now that the system-role template bug is fixed.
#  P3 - Phi-3.5 + DeepSeek-R1-Distill (fix may unlock them too).
# Memory-guarded, marker-resumable. Sequential (no GPU contention).
set +e; cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] OV2 $*" | tee -a "$QDIR/ov2.log"; }
freegb(){ vm_stat|awk '/Pages free/{f=$3+0}/Pages inactive/{i=$3+0}/Pages speculative/{s=$3+0}END{printf "%d",(f+i+s)*16384/1073741824}'; }
cell(){ local model="$1" cond="$2" n="$3" reqgb="$4"; local short
  short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-instruct//;s/-4bit//;s/-it//')
  local mk="$QDIR/.done_ov2_${short}_${cond}"; [[ -f "$mk" ]] && { log "SKIP(done) $short $cond"; return; }
  while [ "$(freegb)" -lt "$reqgb" ]; do log "wait RAM $short $cond need=${reqgb} free=$(freegb)"; sleep 120; done
  local rid="ov2_${short}_${cond}_$(date +%s)"; log "START $short $cond (free=$(freegb)GB)"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated --n "$n" --condition "$cond" \
    --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1; }

# P1 (highest value): powered content-vs-format ablation on the highest-yield open family.
# n=20 already out-powers the existing Qwen3-8B ablation (6.10% base vs 1.46%).
cell mlx-community/Qwen2.5-7B-Instruct-4bit C0_8 20 8    # decoy/WRONG list (key content test)
cell mlx-community/Qwen2.5-7B-Instruct-4bit C0_7 20 8    # structured envelope, no list
# P2: Gemma 4th family (system-role fix) — front-loaded for breadth
cell mlx-community/gemma-2-9b-it-4bit C0 20 9
cell mlx-community/gemma-2-9b-it-4bit C1 20 9
# P3: ladder rung + remaining families (time-permitting)
cell mlx-community/Qwen2.5-7B-Instruct-4bit C0_5 20 8    # naive retry (ladder)
cell mlx-community/Phi-3.5-mini-instruct-4bit C0 20 6
cell mlx-community/Phi-3.5-mini-instruct-4bit C1 20 6
cell mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit C0 20 8
cell mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit C1 20 8
log "===== OVERNIGHT2 QUEUE COMPLETE ====="
