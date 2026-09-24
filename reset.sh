#!/usr/bin/env bash
set -euo pipefail
BASE=/sys/fs/cgroup/metricas-lab02

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

if [[ ! -d "$BASE" ]]; then
    echo "No Lab 02 cgroups to remove."
    exit 0
fi

for cg in "$BASE"/mem-high "$BASE"/mem-max "$BASE"/cpu-half; do
    [[ -d "$cg" ]] || continue
    if [[ -w "$cg/cgroup.kill" ]]; then
        echo 1 > "$cg/cgroup.kill" 2>/dev/null || true
    fi
done

for attempt in {1..20}; do
    busy=0
    for cg in "$BASE"/mem-high "$BASE"/mem-max "$BASE"/cpu-half; do
        [[ -d "$cg" ]] || continue
        if [[ -s "$cg/cgroup.procs" ]]; then
            busy=1
        fi
    done
    (( busy == 0 )) && break
    sleep 0.1
done

for cg in "$BASE"/mem-high "$BASE"/mem-max "$BASE"/cpu-half; do
    [[ -d "$cg" ]] || continue
    rmdir "$cg" 2>/dev/null || {
        echo "ERROR: could not remove $cg; it may still contain a process." >&2
        cat "$cg/cgroup.procs" >&2 || true
        exit 1
    }
done
rmdir "$BASE" 2>/dev/null || true

echo "Lab 02 cgroups removed."
