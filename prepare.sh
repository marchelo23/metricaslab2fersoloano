#!/usr/bin/env bash
set -euo pipefail

BASE=/sys/fs/cgroup/metricas-lab02
ROOT=/sys/fs/cgroup
SELF_DIR=$(cd "$(dirname "$0")" && pwd)

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

if [[ "$(stat -fc %T "$ROOT")" != "cgroup2fs" ]]; then
    echo "ERROR: cgroups v2 is not mounted at /sys/fs/cgroup" >&2
    exit 1
fi

for controller in cpu memory; do
    if ! grep -qw "$controller" "$ROOT/cgroup.controllers"; then
        echo "ERROR: controller '$controller' is not available" >&2
        exit 1
    fi
done

# Start every experiment set with fresh cgroups so event counters begin at zero.
if [[ -d "$BASE" ]]; then
    "$SELF_DIR/reset.sh"
fi

# Make controllers available to the educational subtree. On the course VM they
# are normally already enabled by systemd; adding an already-enabled controller
# is harmless.
echo '+cpu +memory' > "$ROOT/cgroup.subtree_control"

mkdir -p "$BASE"
echo '+cpu +memory' > "$BASE/cgroup.subtree_control"

mkdir -p "$BASE/mem-high" "$BASE/mem-max" "$BASE/cpu-half"

# memory.high experiment: throttle/reclaim boundary, with a generous hard max.
echo $((128 * 1024 * 1024)) > "$BASE/mem-high/memory.high"
echo $((512 * 1024 * 1024)) > "$BASE/mem-high/memory.max"
echo max > "$BASE/mem-high/memory.swap.max"

# memory.max experiment: hard memory limit, no swap for a clearer memcg OOM.
echo max > "$BASE/mem-max/memory.high"
echo $((128 * 1024 * 1024)) > "$BASE/mem-max/memory.max"
echo 0 > "$BASE/mem-max/memory.swap.max"

# CPU experiment: 50 ms of CPU time per 100 ms period = 0.5 CPU.
echo '50000 100000' > "$BASE/cpu-half/cpu.max"

cat <<MSG
Laboratory cgroups prepared under:
  $BASE

Groups:
  mem-high   memory.high=128 MiB, memory.max=512 MiB
  mem-max    memory.max=128 MiB, memory.swap.max=0
  cpu-half   cpu.max=50000 100000
MSG
