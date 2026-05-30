#!/usr/bin/env bash
# Stretch queue: 3 MORE open families on BFCL multi_turn_base (breadth 3->6 lineages).
# Chains cleanly AFTER run_final2 + run_tau_lean (pure sequential, no GPU contention).
# Memory-guarded, marker-resumable. Gemma=Google, Phi=Microsoft, DeepSeek-distill=another lineage.
set +e; cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] STRETCH $*" | tee -a "$QDIR/stretch.log"; }
freegb(){ vm_stat|awk '/Pages free/{f=$3+0}/Pages inactive/{i=$3+0}/Pages speculative/{s=$3+0}END{printf "%d",(f+i+s)*16384/1073741824}'; }
log "waiting for run_final2 + run_tau_lean to finish first..."
while pgrep -f "run_final2.sh" >/dev/null 2>&1 || pgrep -f "run_tau_lean.sh" >/dev/null 2>&1; do sleep 200; done
log "prior queues done - running 3 more open families on BFCL (breadth)."
cell(){ local model="$1" cond="$2" n="$3" reqgb="$4"; local short
  short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-instruct//;s/-4bit//;s/-it//')
  local mk="$QDIR/.done_stretch_${short}_${cond}"; [[ -f "$mk" ]] && { log "SKIP(done) $short $cond"; return; }
  while [ "$(freegb)" -lt "$reqgb" ]; do log "wait RAM $short $cond need=${reqgb} free=$(freegb)"; sleep 120; done
  local rid="stretch_${short}_${cond}_$(date +%s)"; log "START $short $cond (free=$(freegb)GB)"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated --n "$n" --condition "$cond" \
    --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1; }
for M in mlx-community/gemma-2-9b-it-4bit mlx-community/Phi-3.5-mini-instruct-4bit mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit; do
  cell "$M" C0 20 8     # baseline (does this family fabricate?)
  cell "$M" C1 20 8     # RVR (does the fix generalize?)
done
log "===== STRETCH QUEUE COMPLETE ====="
