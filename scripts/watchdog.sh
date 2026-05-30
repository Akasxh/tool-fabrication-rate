#!/usr/bin/env bash
# Cron watchdog: keeps the overnight experiment pipeline alive across failures.
# Relaunches caffeinate + the experiment queues if (and only if) they died AND
# haven't logged completion. The bash queue scripts persist across cells, so a
# missing pgrep means genuine death — markers make relaunches resume safely.
ROOT="/Users/cero/Desktop/PROJECTS/icml"
cd "$ROOT" 2>/dev/null || exit 0
QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR"; LOG="$QDIR/watchdog.log"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }
# single-instance guard for the watchdog itself
exec 9>"$QDIR/.watchdog.lock"; flock -n 9 || exit 0
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
# 4) run_stretch (3 more open families, breadth) — relaunch if dead & not complete
if [ -f "$ROOT/scripts/run_stretch.sh" ] && ! pgrep -f "run_stretch.sh" >/dev/null 2>&1 && ! grep -q "STRETCH QUEUE COMPLETE" "$QDIR/stretch.log" 2>/dev/null; then
  nohup bash "$ROOT/scripts/run_stretch.sh" >/dev/null 2>&1 & echo "$(ts) RELAUNCH run_stretch" >>"$LOG"
fi
echo "$(ts) tick: caffeinate=$(pgrep -f "caffeinate -i -d -m -s" 2>/dev/null | wc -l | tr -d " ") final2=$(pgrep -f run_final2.sh 2>/dev/null | wc -l | tr -d " ") taulean=$(pgrep -f run_tau_lean.sh 2>/dev/null | wc -l | tr -d " ") stretch=$(pgrep -f run_stretch.sh 2>/dev/null | wc -l | tr -d " ") freeGB=$(vm_stat|awk '/Pages free/{f=$3+0}/Pages inactive/{i=$3+0}/Pages speculative/{s=$3+0}END{printf "%d",(f+i+s)*16384/1073741824}')" >>"$LOG"
