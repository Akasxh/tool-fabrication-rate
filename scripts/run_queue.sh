#!/usr/bin/env bash
# Sequential M5 experiment queue for the TEHR spotlight revision.
# Value-ordered: decoy ablation + tightened curve land first.
# Resumable: each cell writes a .done marker; re-running skips completed cells.
# Robust: a failed cell is logged and skipped, never kills the queue.
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"
PY="$ROOT/harness/.venv/bin/python"
QDIR="$ROOT/results/_queue"
mkdir -p "$QDIR/logs"
STATUS="$QDIR/STATUS.tsv"
TS_START=$(date +%s)
echo -e "ts\tstep\tmodel\tcond\tresult" >> "$STATUS"

log()    { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$QDIR/queue.log"; }

run_cell() {
  # args: step_label  model_repo  condition  n
  local step="$1" model="$2" cond="$3" n="$4"
  local short; short=$(echo "$model" | sed 's#.*/##; s/Qwen3-//; s/-4bit//')
  local marker="$QDIR/.done_${step}_${short}_${cond}"
  if [[ -f "$marker" ]]; then log "SKIP (done): $step $short $cond"; return; fi
  local rid="qwen3_${short}_${cond}_${step}_$(date +%s)"
  local lg="$QDIR/logs/${rid}.log"
  log "START: $step model=$short cond=$cond n=$n -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py \
    --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated \
    --n "$n" --condition "$cond" --remove-target \
    --run-id "$rid" > "$lg" 2>&1
  local rc=$?
  local res; res=$(grep -E "tehr=[0-9]+/" "$lg" | tail -4 | tr '\n' ' ')
  if [[ $rc -eq 0 ]]; then touch "$marker"; log "DONE: $step $short $cond | $res"
  else log "FAIL(rc=$rc): $step $short $cond (see $lg)"; res="FAIL rc=$rc"; fi
  echo -e "$(date +%s)\t$step\t$short\t$cond\t$res" >> "$STATUS"
  # refresh aggregate so PROGRESS reflects latest
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py > "$QDIR/last_aggregate.txt" 2>&1
}

log "===== QUEUE START ====="

# 1) 8B full 5-condition ablation (incl. C0_8 decoy) — spotlight ablation
for C in C0_8 C0_7 C1 C0 C0_5; do run_cell s1ab8b  mlx-community/Qwen3-8B-4bit  "$C" 25; done
# 2) 14B curve N-expansion (tighten the peak; locked at 1.64% = 6/366)
run_cell s2c14b mlx-community/Qwen3-14B-4bit C0 50
# 3) 32B curve N-expansion (tighten the 0% collapse)
run_cell s3c32b mlx-community/Qwen3-32B-4bit C0 50
# 4) 14B full 5-condition ablation (ablation at the peak tier)
for C in C0_8 C0_7 C1 C0 C0_5; do run_cell s4ab14b mlx-community/Qwen3-14B-4bit "$C" 25; done
# 5) 4B full 5-condition ablation
for C in C0_8 C0_7 C1 C0 C0_5; do run_cell s5ab4b  mlx-community/Qwen3-4B-4bit  "$C" 25; done
# 6) Quantization confound (only if weights present; downloader runs concurrently)
for M in Qwen3-8B-8bit Qwen3-8B-bf16 Qwen3-14B-8bit; do
  if "$PY" -c "import glob,sys; sys.exit(0 if glob.glob('$HOME/.cache/huggingface/hub/models--mlx-community--$M') else 1)"; then
    run_cell s6quant "mlx-community/$M" C0 25
  else log "SKIP (not downloaded yet): $M"; fi
done
# 7) 8B curve reference at matched n=50
run_cell s7c8b  mlx-community/Qwen3-8B-4bit  C0 50

log "===== QUEUE COMPLETE (elapsed $(( ($(date +%s)-TS_START)/60 )) min) ====="
