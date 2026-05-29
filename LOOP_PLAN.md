# Overnight Ralph-Loop Playbook — converge toward ICML main-track by **May 31 AoE**, keep the paper **always submittable**

Goal: iterate autonomously while experiments land; fold each result into the paper; never leave it broken. The honest ceiling is borderline-main-track — push it, don't fake it.

## Each iteration (pace to experiment timescale; ~check every 20–40 min)
1. **Keep-alive:** ensure `caffeinate -i -d -m -s -t 100000` is running (Mac awake). If not: relaunch it. Else experiments pause.
2. **Queues healthy:** `run_tau_grid.sh` + `run_final2.sh` alive?
   - If a queue **died** mid-way → relaunch it (`nohup bash scripts/<q>.sh &`); markers make it resume, no rework.
   - If a cell is **stuck** (trace frozen >15 min) → `pkill` that specific `run_probe.py` child (the queue's `cell()` then proceeds to the next). Never kill the queue script for a stuck cell.
   - `run_final2.sh` is memory-guarded (skips big models if RAM low) — trust it; don't force bf16/14B-8bit if free RAM < ~19GB.
3. **Aggregate:** `PYTHONPATH=. harness/.venv/bin/python scripts/aggregate_all.py`. Analyze tau-bench SEPARATELY (`results_tau/`, via `analyze_run.py`) — **never pool tau/bf16/cross-family into the BFCL headline pool.**
4. **Integrate NEW results as they land** (use ONLY aggregator/analyze numbers; never invent):
   - **Qwen3 tau-bench gap** (`results_tau/`): the 2nd-benchmark result → §5 + the +1-page frontier/gap table. *The swing result for main-track.*
   - **Quant ladder** (8bit/bf16): → §5 + upgrade Limitations from "cannot disentangle quantization" to the measured control.
   - **Cross-family** (Llama/Mistral/Qwen2.5): → §5 breadth (2nd/3rd open family + RVR generalization).
   - Per integration: re-lock → `tectonic main.tex` (2 passes, body ≤8pp, 0 undefined) → verify reproduces → refresh `paper/main_camera_ready.pdf` → **commit**.
5. **Paper-ready invariant:** after EVERY change, the PDF must build clean. If a change breaks it → `git checkout` the file / revert to last good commit. `main_camera_ready.pdf` is always submittable. Tag good states (`git tag -f overnight-<n>`).
6. **When all queued experiments are done:** final pass — integrate staged `paper/_staging/plus_page/` (+ scaling figure back to body, frontier table, response-to-reviewers, gap result, quant ladder, cross-family) with the gap-led thesis → run the persona panel once more (Claude personas + a gpt frontier review) → fix the top 3 issues → final compile + tag.
7. **Stop / surface:** end the loop when all experiments are integrated, the panel has run, and the paper builds+reproduces. **Surface to the user** (don't silently continue) if: a thesis-changing result appears (e.g., the gap does NOT replicate on tau-bench, or the 14B peak collapses), the paper can't be made to build, or the deadline is near and a decision is needed.
8. **Never:** leave the paper non-building · pool tau/bf16/cross-family into the BFCL headline · invent/round-trip a number not from the aggregator · re-introduce a memory thrash · touch author identity beyond what's given (S Akash, Shine Gupta, IIT Patna).

## Current state at loop start
- Camera-ready: reproduces aggregator, builds clean, 8pp limit OK, tagged `workshop-ready-honest`; `main_camera_ready.pdf` submittable.
- Running: tau grid (Qwen3-8B gap test now → 14B next) → `run_final2` (8bit + cross-family fit now; 14B-8bit/bf16 when RAM frees).
- Locked headline: Anthropic 0/2592, OpenAI 0/2117, Qwen3 curve peak 14B 1.64% (6/366), RVR 20/1417 vs 0/945 p=3.5e-5, 153 tests, $82.
- Pending swing results: Qwen3 tau-bench gap · quant ladder · cross-family.
