#!/usr/bin/env bash
# LEAN ~1-day compute (replaces the multi-day n=100 queues). Only the
# genuinely-missing high-value cells; everything else uses existing data.
#   1) A2 reflection arm  -> completes the ablation ladder ("is RVR just reflection?")
#   2) quantization control (8B 4/8/bf16 + 14B-8bit) -> breaks the #1 main-track confound
#   3) 14B C0 n=25 event-boost on the peak tier
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"; QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] LEAN $*" | tee -a "$QDIR/lean.log"; }
run_cell(){ # model cond n
  local model="$1" cond="$2" n="$3"
  local short; short=$(echo "$model" | sed 's#.*/##; s/Qwen3-//; s/-4bit//')
  local marker="$QDIR/.done_lean_${short}_${cond}"
  [[ -f "$marker" ]] && { log "SKIP $short $cond"; return; }
  local rid="qwen3_${short}_${cond}_lean_$(date +%s)"
  log "START $short $cond n=$n -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated \
    --n "$n" --condition "$cond" --remove-target --run-id "$rid" > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$marker"
  log "DONE $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log" | tail -4 | tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1
}
log "===== LEAN QUEUE START ====="
run_cell mlx-community/Qwen3-8B-4bit A2 25                       # ablation ladder
for V in Qwen3-8B-8bit Qwen3-8B-bf16 Qwen3-14B-8bit; do          # quant confound
  if [ -d "$HOME/.cache/huggingface/hub/models--mlx-community--$V" ]; then
    run_cell "mlx-community/$V" C0 25
  else log "SKIP (not downloaded): $V"; fi
done
run_cell mlx-community/Qwen3-14B-4bit C0 25                      # peak event-boost
log "===== LEAN QUEUE COMPLETE ====="
