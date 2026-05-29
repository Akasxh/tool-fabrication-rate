#!/usr/bin/env bash
# Download MLX quantization variants for the confound spot-check (network-bound;
# safe to run concurrently with the inference queue). 14B-bf16 is intentionally
# omitted — 29.5GB exceeds usable unified memory on a 32GB M5.
set +e
cd "$(dirname "$0")/.." || exit 1
HF="$(pwd)/harness/.venv/bin/hf"
LOG="$(pwd)/results/_queue/download.log"
mkdir -p "$(dirname "$LOG")"
for V in Qwen3-8B-8bit Qwen3-8B-bf16 Qwen3-14B-8bit; do
  echo "[$(date '+%H:%M:%S')] downloading mlx-community/$V" >> "$LOG"
  "$HF" download "mlx-community/$V" >> "$LOG" 2>&1
  echo "[$(date '+%H:%M:%S')] done mlx-community/$V (rc=$?)" >> "$LOG"
done
echo "[$(date '+%H:%M:%S')] ALL DOWNLOADS COMPLETE" >> "$LOG"
