#!/usr/bin/env bash
# Memory-AWARE final queue: quant precision ladder (4/8/bf16) + cross-family.
# Each cell waits for enough free RAM before loading its model, and SKIPS
# (never thrashes) if RAM stays too low. Big models run opportunistically once
# the API frontier frees memory. Chains after the tau-bench gap test.
set +e; cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] FINAL2 $*" | tee -a "$QDIR/final2.log"; }
freegb(){ vm_stat | awk '/Pages free/{f=$3+0}/Pages inactive/{i=$3+0}/Pages speculative/{s=$3+0}END{printf "%d",(f+i+s)*16384/1073741824}'; }
log "waiting for tau grid (Qwen3 gap test) to finish first…"
while pgrep -f "run_tau_grid.sh" >/dev/null 2>&1; do sleep 200; done
log "tau gap test done — running memory-guarded quant ladder + cross-family. free=$(freegb)GB"
cell(){ # model cond n reqgb
  local model="$1" cond="$2" n="$3" reqgb="$4"; local short; short=$(echo "$model"|sed 's#.*/##;s/-Instruct//;s/-4bit//')
  local mk="$QDIR/.done_final2_${short}_${cond}"; [[ -f "$mk" ]] && { log "SKIP(done) $short $cond"; return; }
  local t=0
  while [ "$(freegb)" -lt "$reqgb" ]; do t=$((t+1)); [ $t -gt 12 ] && { log "SKIP(low-mem) $short $cond: free $(freegb)GB < ${reqgb}GB after 24min"; return; }
    log "  hold $short $cond: free $(freegb)GB < ${reqgb}GB, waiting…"; sleep 120; done
  local rid="final2_${short}_${cond}_$(date +%s)"; log "START $short $cond (free=$(freegb)GB)"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated --n "$n" --condition "$cond" \
    --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$mk"; log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log"|tail -4|tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1; }
# fit-now cells first (req GB = model size + ~3 headroom)
cell mlx-community/Qwen3-8B-8bit C0 25 12                                   # 8.7GB
for M in mlx-community/Llama-3.1-8B-Instruct-4bit mlx-community/Mistral-7B-Instruct-v0.3-4bit; do
  cell "$M" C0 20 8; cell "$M" C1 20 8; done                                # ~5GB
cell mlx-community/Qwen2.5-7B-Instruct-4bit C1 20 8                         # ~4.5GB
# tight cells — only run when RAM frees (else skip, no thrash)
cell mlx-community/Qwen3-14B-8bit C0 25 19                                  # 15.7GB
cell mlx-community/Qwen3-8B-bf16  C0 25 19                                  # 16.4GB (the proper full-precision control)
log "===== FINAL2 COMPLETE (free=$(freegb)GB) ====="
