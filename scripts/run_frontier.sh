#!/usr/bin/env bash
# Non-Anthropic FRONTIER ladder (main-track gate #1, vendor axis).
# Within-OpenAI size ladder (nano->mini->full) + frontier, on the distractor
# probe. API-only — runs in parallel with the M5 queue, no GPU contention.
# Tests: does the 0%-hallucination hold for a 2nd frontier vendor? Does the
# non-monotonic SCALE effect replicate within OpenAI?
set +e
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"; PY="$ROOT/harness/.venv/bin/python"
QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR/logs"
set -a; [ -f "$ROOT/.env.local" ] && . "$ROOT/.env.local"; set +a
log(){ echo "[$(date '+%H:%M:%S')] FR $*" | tee -a "$QDIR/frontier.log"; }

# import-safety check (adapter was just edited)
"$PY" -c "import harness.adapters.openai_adapter" 2>>"$QDIR/frontier.log" || { log "IMPORT FAIL — aborting"; exit 1; }

MODELS="gpt-4.1-nano gpt-4.1-mini gpt-4.1 gpt-4o-mini gpt-4o gpt-5-nano gpt-5-mini gpt-5 gpt-5.5"
N=20
log "===== FRONTIER LADDER START (n=$N x4 distractors x $(echo $MODELS|wc -w) models) ====="
for M in $MODELS; do
  short=$(echo "$M" | sed 's/[.]/_/g')
  marker="$QDIR/.done_frontier_${short}"
  [[ -f "$marker" ]] && { log "SKIP $M"; continue; }
  rid="frontier_${short}_C0_$(date +%s)"
  log "START $M -> $rid"
  PYTHONPATH="$ROOT" "$PY" scripts/run_probe.py --models "$M" \
    --distractor-types near_name,synonym,matched_random,unrelated \
    --n "$N" --condition C0 --remove-target --run-id "$rid" \
    > "$QDIR/logs/${rid}.log" 2>&1
  rc=$?
  res=$(grep -E "tehr=[0-9]+/" "$QDIR/logs/${rid}.log" | tail -4 | tr '\n' ' ')
  spend=$(grep -oE "spend=\\\$[0-9.]+" "$QDIR/logs/${rid}.log" | tail -1)
  [[ $rc -eq 0 ]] && touch "$marker"
  log "DONE  $M (rc=$rc $spend) | $res"
  PYTHONPATH="$ROOT" "$PY" scripts/aggregate_all.py >/dev/null 2>&1
done
log "===== FRONTIER LADDER COMPLETE ====="
# quick summary
"$PY" - <<'PY' 2>>"$QDIR/frontier.log"
import json,glob
from collections import defaultdict
agg=defaultdict(lambda:[0,0])
for f in glob.glob("results/frontier_*/**/*.jsonl",recursive=True):
    for line in open(f):
        if not line.strip():continue
        r=json.loads(line)
        if r["tool_call_status"]=="hallucinated": agg[r["model"]][0]+=1
        if r["tool_call_status"] in ("hallucinated","parse_fail") or (r["tool_call_status"]=="executed" and r.get("parsed_tool_call")): agg[r["model"]][1]+=1
print("=== FRONTIER TEHR summary ===")
for m,(h,n) in sorted(agg.items()):
    print(f"  {m:16s} {h}/{n} = {100*h/n:.2f}%" if n else f"  {m:16s} 0/0")
PY
cat "$QDIR/frontier.log" | tail -15
