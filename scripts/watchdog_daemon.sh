#!/usr/bin/env bash
# Self-looping keep-alive daemon. Runs the single-tick watchdog every 300s.
# Launched as a nohup child of the granted Terminal/Claude session so it
# inherits Full Disk Access to the ~/Desktop project tree (launchd cannot:
# it hits TCC "Operation not permitted" exec'ing scripts under ~/Desktop).
# Survives the session ending (nohup + reparent to launchd). Single-instance.
ROOT="/Users/cero/Desktop/PROJECTS/icml"
QDIR="$ROOT/results/_queue"; mkdir -p "$QDIR"
exec 8>"$QDIR/.watchdog_daemon.lock"; flock -n 8 || exit 0
echo "$(date '+%Y-%m-%d %H:%M:%S') DAEMON START pid=$$" >>"$QDIR/watchdog.log"
while true; do
  bash "$ROOT/scripts/watchdog.sh" 2>/dev/null
  sleep 300
done
