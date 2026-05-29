#!/usr/bin/env bash
# Follow-on queue: MAIN-TRACK gate #2 (multiply event count, N>=100/cell on the
# most-scrutinized non-zero Qwen3 tiers) + gate #1 vendor axis (non-Anthropic
# frontier probe, auto-runs ONLY if a key is present).
# Chains AFTER run_queue.sh so the two never contend for the M5.
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"
QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
log(){ echo "[$(date '+%H:%M:%S')] Q2 $*" | tee -a "$QDIR/queue2.log"; }

# Wait for the primary queue to finish (no GPU contention).
log "waiting for run_queue.sh to drain before starting high-N follow-on…"
while pgrep -f "run_queue.sh" >/dev/null 2>&1; do sleep 300; done
log "primary queue drained — starting follow-on."

run_cell(){ # step model cond n
  local step="$1" model="$2" cond="$3" n="$4"
  local short; short=$(echo "$model" | sed 's#.*/##; s/Qwen3-//; s/-4bit//')
  local marker="$QDIR/.done_${step}_${short}_${cond}"
  [[ -f "$marker" ]] && { log "SKIP $step $short $cond"; return; }
  local rid="qwen3_${short}_${cond}_${step}_$(date +%s)"
  log "START $step $short $cond n=$n -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$model" \
    --distractor-types near_name,synonym,matched_random,unrelated \
    --n "$n" --condition "$cond" --remove-target --run-id "$rid" \
    > "$QDIR/logs/${rid}.log" 2>&1
  [[ $? -eq 0 ]] && touch "$marker"
  log "DONE  $step $short $cond | $(grep -E 'tehr=[0-9]+/' "$QDIR/logs/${rid}.log" | tail -4 | tr '\n' ' ')"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1
}

# Gate #2 — event multiplication (N>=100/cell) on the peak tier (14B) and the
# ablation tier (8B, all conditions so "registry is decorative" rests on >0 events).
run_cell q2n100 mlx-community/Qwen3-14B-4bit C0  100
run_cell q2n100 mlx-community/Qwen3-8B-4bit  C0  100
for C in C0_7 C0_8 C1; do run_cell q2n100 mlx-community/Qwen3-8B-4bit "$C" 100; done

# Gate #1 vendor axis — non-Anthropic FRONTIER probe. Auto-runs only if a key
# exists; otherwise logs the block so it's obvious what's pending.
if grep -q "^OPENAI_API_KEY=" "$ROOT/.env.local" 2>/dev/null || [ -n "$OPENAI_API_KEY" ]; then
  log "OPENAI key present — running non-Anthropic frontier probe (vendor confound break)"
  set -a; [ -f "$ROOT/.env.local" ] && . "$ROOT/.env.local"; set +a
  for M in gpt-4.1 gpt-5; do
    rid="frontier_${M}_C0_$(date +%s)"
    log "START frontier $M"
    PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$M" \
      --distractor-types near_name,synonym,matched_random,unrelated \
      --n 15 --condition C0 --remove-target --run-id "$rid" \
      > "$QDIR/logs/${rid}.log" 2>&1
    log "DONE frontier $M | $(grep -E 'tehr=' "$QDIR/logs/${rid}.log" | tail -4 | tr '\n' ' ')"
  done
else
  log "NO non-Anthropic key (.env.local) — FRONTIER PROBE PENDING. Add OPENAI_API_KEY or GEMINI key and re-run scripts/run_queue2.sh to break the vendor confound (top main-track gate)."
fi
log "===== FOLLOW-ON QUEUE COMPLETE ====="
