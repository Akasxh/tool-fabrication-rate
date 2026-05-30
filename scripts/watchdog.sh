#!/usr/bin/env bash
# Cron watchdog: keeps the overnight experiment pipeline alive across failures.
# Relaunches caffeinate + the experiment queues if (and only if) they died AND
# haven't logged completion. The bash queue scripts persist across cells, so a
# missing pgrep means genuine death — markers make relaunches resume safely.
ROOT="/Users/cero/Desktop/PROJECTS/icml"
cd "$ROOT" 2>/dev/null || exit 0
QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR"; LOG="$QDIR/watchdog.log"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }
# NOTE: no flock here. The daemon (watchdog_daemon.sh) already holds a single-
# instance lock and calls this script sequentially, so a second lock is
# redundant — and worse, its fd leaks into the nohup'd queue children below,
# which then pin the lock forever and silently no-op every future tick.
# 1) Mac awake
pgrep -f "caffeinate -i -d -m -s" >/dev/null 2>&1 || { nohup caffeinate -i -d -m -s -t 100000 >/dev/null 2>&1 & echo "$(ts) RELAUNCH caffeinate" >>"$LOG"; }
# 2) run_final2 (quant ladder + cross-family) — relaunch if dead & not complete
if ! pgrep -f "run_final2.sh" >/dev/null 2>&1 && ! grep -q "FINAL2 COMPLETE" "$QDIR/final2.log" 2>/dev/null; then
  nohup bash "$ROOT/scripts/run_final2.sh" >/dev/null 2>&1 & echo "$(ts) RELAUNCH run_final2 (resume via markers)" >>"$LOG"
fi
# 3) run_tau_lean (lean 2nd-benchmark gap) — relaunch if dead & not complete
if ! pgrep -f "run_tau_lean.sh" >/dev/null 2>&1 && ! grep -q "LEAN TAU GAP COMPLETE" "$QDIR/tau_lean.log" 2>/dev/null; then
  nohup bash "$ROOT/scripts/run_tau_lean.sh" >/dev/null 2>&1 & echo "$(ts) RELAUNCH run_tau_lean" >>"$LOG"
fi
# 4) run_overnight2 (powered Qwen2.5 ablation + unlocked families) — relaunch if dead & not complete
if [ -f "$ROOT/scripts/run_overnight2.sh" ] && ! pgrep -f "run_overnight2.sh" >/dev/null 2>&1 && ! grep -q "OVERNIGHT2 QUEUE COMPLETE" "$QDIR/ov2.log" 2>/dev/null; then
  nohup bash "$ROOT/scripts/run_overnight2.sh" >/dev/null 2>&1 & echo "$(ts) RELAUNCH run_overnight2" >>"$LOG"
fi
echo "$(ts) tick: caffeinate=$(pgrep -f "caffeinate -i -d -m -s" 2>/dev/null | wc -l | tr -d " ") ov2=$(pgrep -f run_overnight2.sh 2>/dev/null | wc -l | tr -d " ") freeGB=$(vm_stat|awk '/Pages free/{f=$3+0}/Pages inactive/{i=$3+0}/Pages speculative/{s=$3+0}END{printf "%d",(f+i+s)*16384/1073741824}')" >>"$LOG"
