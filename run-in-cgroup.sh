#!/usr/bin/env bash
set -euo pipefail

BASE=/sys/fs/cgroup/metricas-lab02

if (( $# < 2 )); then
    echo "Usage: $0 {mem-high|mem-max|cpu-half} COMMAND [ARG...]" >&2
    exit 2
fi

group=$1
shift
cg="$BASE/$group"

if [[ ! -d "$cg" ]]; then
    echo "ERROR: $cg does not exist. Run ./prepare.sh first." >&2
    exit 1
fi

# Move this shell to the selected cgroup; exec makes the workload inherit it.
sudo sh -c "printf '%s\\n' '$$' > '$cg/cgroup.procs'"
exec "$@"
