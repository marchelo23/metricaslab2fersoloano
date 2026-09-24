#!/usr/bin/env bash
set -uo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$LAB_DIR" || exit 1

BASE=/sys/fs/cgroup/metricas-lab02
I_F=/tmp/lab2_ini.txt
F_F=/tmp/lab2_fin.txt
PAUSE=0
[ "${NONINTERACTIVE:-0}" = "1" ] && PAUSE=1

hr()  { printf '\n%80s\n' '' | tr ' ' '='; }
sec() { hr; printf '## %s\n' "$1"; }
cap() { printf '\n   >>>> %s <<<<\n' "$1"; }
show(){ printf '\n$ %s\n' "$*"; "$@"; }

pause() {
  if [ "$PAUSE" = "1" ]; then sleep 3; return; fi
  echo
  read -r -p "   [Presione ENTER para continuar / Ctrl+C para salir] " _
  echo
}

delta() {
  local k=$1 vi vf
  vi=$(awk -vkey="$k" '$1==key{print $2}' "$I_F" 2>/dev/null); vi=${vi:-0}
  vf=$(awk -vkey="$k" '$1==key{print $2}' "$F_F" 2>/dev/null); vf=${vf:-0}
  printf '  %-14s inicial=%-6s final=%-6s d=%s\n' "$k" "$vi" "$vf" "$((vf-vi))"
}

require_prepare() {
  if [ ! -d "$BASE/mem-high" ]; then
    echo "  (los cgroups no estan creados: ejecutando ./prepare.sh)"
    ./prepare.sh
  fi
}

portada() {
  sec "LABORATORIO 2 - Aislamiento y control de recursos en Linux"
  echo "  Maquina: $(uname -srm)   $(date)"
  echo "  cgroups montados como: $(stat -fc %T /sys/fs/cgroup)  (debe decir cgroup2fs)"
  echo "  Operando sobre el subtree $BASE (no se toca nada fuera de el)."
  echo "  Los comandos de listado de procesos (Inv. 1) estan filtrados para"
  echo "  no volcar los procesos del host; el resto del lab no lista procesos."
}

grabar_help() {
  echo
  echo "  Grabar la sesion (reproduccion paso a paso):"
  echo "    script --timing=lab2.time -a lab2.session bash lab2.sh"
  echo "    scriptreplay --timing=lab2.time lab2.session"
  echo "  (script/scriptreplay del paquete util-linux; la reproduccion reimprime"
  echo "   la salida guardada con su ritmo original, no re-ejecuta los comandos.)"
}

inv1() {
  sec "INVESTIGACION 1 - PID namespace y punto de observacion"
  echo "  Se reproducen las dos vistas (dentro del namespace y del host) en esta"
  echo "  misma terminal. Para replicar el flujo original en dos terminales:"
  echo "    Term A: sudo unshare --pid --fork --mount-proc bash   (luego printf ...; sleep 120)"
  echo "    Term B: ps -eo pid,ppid,comm,args --forest | grep unshare|sleep 120  (filtrado)"
  echo
  sudo pkill -f 'unshare --pid --fork --mount-proc' 2>/dev/null

  cap "CAPTURA 1 - Vista desde dentro del namespace (equivalente Terminal A)"
  printf '\n$ sudo unshare --pid --fork --mount-proc bash -c '\''printf "PID visto dentro: %%s\\n" "$$"; sleep 120'\'' &\n'
  sudo unshare --pid --fork --mount-proc bash -c 'printf "PID visto dentro: %s\n" "$$"; sleep 120' &
  ns_launcher=$!

  S=""
  echo "  (esperando que el proceso arranque; si sudo pide password, ingresala)"
  for _ in $(seq 1 60); do
    S=$(ps -eo pid,args | awk '$2=="sleep" && $3=="120"{print $1; exit}')
    [ -n "$S" ] && break
    sleep 0.5
  done
  if [ -z "$S" ]; then
    echo "  ERROR: no se detecto el proceso 'sleep 120' del namespace. Reintenta."
    return 1
  fi
  B=$(ps -o ppid= -p "$S" | tr -d ' ')
  echo "  (el bash del namespace tiene PID host=$B; su 'sleep' interno PID host=$S)"
  pause

  cap "CAPTURA 2 - Vista desde el host (jerarquia filtrada y NSpid)"
  echo "  Ej: host=$(hostname). Solo se muestran las lineas del unshare/bash/sleep."
  printf '\n$ ps -eo pid,ppid,comm,args --forest | grep -E "PID|unshare|sleep 120"\n'
  ps -eo pid,ppid,comm,args --forest | grep -E "PID|unshare|sleep 120"
  printf '\n$ grep "^NSpid:" /proc/%s/status\n' "$B"
  grep '^NSpid:' "/proc/$B/status"
  printf '\n$ grep "^NSpid:" /proc/%s/status\n' "$S"
  grep '^NSpid:' "/proc/$S/status"
  echo
  echo "  Interpretacion rapida: el mismo proceso se ve como PID 1 dentro del"
  echo "  namespace y como PID $B desde el host (la linea NSpid lista ambos)."
  pause

  sudo kill "$S" "$B" "$ns_launcher" 2>/dev/null
  sudo pkill -f 'unshare --pid --fork --mount-proc' 2>/dev/null
  echo "  (namespace cerrado)"
}

inv2() {
  sec "INVESTIGACION 2 - memory.high y presion de memoria"
  require_prepare
  G="$BASE/mem-high"
  echo "  Grupo: $G  (memory.high=128 MiB, memory.max=512 MiB)"
  echo "  El workload reservara 256 MiB: por encima de memory.high, debajo de max."
  echo
  cap "CAPTURA 3 (pre) - Configuracion y contadores iniciales"
  show cat "$G/memory.high"
  show cat "$G/memory.max"
  show cat "$G/memory.current"
  show cat "$G/memory.events"
  cp "$G/memory.events" "$I_F"
  echo
  echo "  >>> PREDICCION: anota antes de continuar lo que esperas que ocurra al"
  echo "      superar 128 MiB (terminacion? supera el valor? que contadores cambian?)."
  pause

  printf '\n$ ./run-in-cgroup.sh mem-high ./mem_work 256 100 5\n'
  ./run-in-cgroup.sh mem-high ./mem_work 256 100 5 | tee /tmp/lab2_high.txt
  rc=${PIPESTATUS[0]}
  cp "$G/memory.events" "$F_F"
  printf '\nexit=%s\n' "$rc"
  echo
  cap "CAPTURA 3 (post) - Contadores finales de memory.events"
  show cat "$G/memory.events"
  printf '\n  Uso final de memoria del grupo:\n'
  show cat "$G/memory.current"
  show cat "$G/memory.peak"
  echo
  echo "  Incrementos (final - inicial):"
  delta high
  delta max
  delta oom
  delta oom_kill
  echo
  echo "  Respuestas: allocation_complete? $(grep -c 'allocation_complete' /tmp/lab2_high.txt)"
  echo "              completed normally?  $(grep -c 'completed normally' /tmp/lab2_high.txt)"
  pause
}

inv3() {
  sec "INVESTIGACION 3 - memory.max y OOM"
  require_prepare
  G="$BASE/mem-max"
  echo "  Grupo: $G  (memory.max=128 MiB, memory.swap.max=0, memory.high=max)"
  echo "  El workload volvera a intentar reservar 256 MiB."
  echo
  cap "CAPTURA 4 (pre) - Configuracion y contadores iniciales"
  show cat "$G/memory.max"
  show cat "$G/memory.swap.max"
  show cat "$G/memory.events"
  cp "$G/memory.events" "$I_F"
  echo
  echo "  >>> PREDICCION: que esperas que pase al superar 128 MiB? que cambios"
  echo "      en memory.events? termina por decision propia o por el mecanismo?"
  pause

  printf '\n$ ./run-in-cgroup.sh mem-max ./mem_work 256 100 5\n'
  ./run-in-cgroup.sh mem-max ./mem_work 256 100 5
  rc=$?
  cp "$G/memory.events" "$F_F"
  printf '\nexit= %s\n' "$rc"
  echo
  cap "CAPTURA 4 (post) - Contadores finales relevantes de memory.events"
  show cat "$G/memory.events"
  echo
  echo "  Incrementos (final - inicial):"
  delta max
  delta oom
  delta oom_kill
  echo
  echo "  Ultimo 'allocated_mib' visible: revisar salida arriba (esperado cercano a 128)."
  echo "  allocation_complete NO debe aparecer; 'completed normally' NO debe aparecer."
  pause
}

inv4() {
  sec "INVESTIGACION 4 - cpu.max y throttling"
  require_prepare
  G="$BASE/cpu-half"
  echo "  Grupo: $G  (cpu.max=50000 100000  = 0.5 CPU por periodo de 100 ms)"
  echo
  cap "CAPTURA 5 - Baseline fuera del cgroup"
  printf '\n$ ./cpu_work 8\n'
  ./cpu_work 8 | tee /tmp/lab2_base.txt
  pause

  cap "CAPTURA 6 (pre) - Configuracion cpu.max y cpu.stat inicial"
  show cat "$G/cpu.max"
  cp "$G/cpu.stat" "$I_F"
  show cat "$G/cpu.stat"
  echo
  echo "  >>> PREDICCION: que cambio esperas en el trabajo completado con la cuota"
  echo "      y que evidencia buscarias en cpu.stat?"
  pause

  cap "CAPTURA 6 (post) - Ejecucion limitada y cpu.stat final"
  printf '\n$ ./run-in-cgroup.sh cpu-half ./cpu_work 8\n'
  ./run-in-cgroup.sh cpu-half ./cpu_work 8 | tee /tmp/lab2_cuota.txt
  cp "$G/cpu.stat" "$F_F"
  printf '\n$ cat %s/cpu.stat   (final)\n' "$G"
  show cat "$G/cpu.stat"
  echo
  echo "  Incrementos (final - inicial):"
  delta usage_usec
  delta nr_throttled
  delta throttled_usec
  echo
  ib=$(awk -F= '/^iterations=/{v=$2} END{print v+0}' /tmp/lab2_base.txt)
  iq=$(awk -F= '/^iterations=/{v=$2} END{print v+0}' /tmp/lab2_cuota.txt)
  eb=$(awk -F= '/^elapsed_s=/{v=$2} END{print v+0}' /tmp/lab2_base.txt)
  eq=$(awk -F= '/^elapsed_s=/{v=$2} END{print v+0}' /tmp/lab2_cuota.txt)
  razon=$(awk -v a="$iq" -v b="$ib" 'BEGIN{ if (b>0) printf "%.3f", a/b; else print "n/d" }')
  printf '  elapsed_s      baseline=%.4f   cpu-half=%.4f\n' "$eb" "$eq"
  printf '  iterations     baseline=%s   cpu-half=%s\n' "$ib" "$iq"
  printf '  razon de trabajo = iterations(cuota) / iterations(baseline) = %s\n' "$razon"
  pause
}

prepare_lab() {
  sec "PREPARANDO cgroups"
  ./prepare.sh
}

reset_lab() {
  sec "LIMPIANDO cgroups (reset.sh)"
  ./reset.sh
}

resumen_capturas() {
  sec "RESUMEN DE CAPTURAS OBLIGATORIAS"
  printf '  1. Vista dentro del PID namespace (PID impreso por el bash del unshare)\n'
  printf '  2. Vista desde el host: jerarquia filtrada + linea NSpid\n'
  printf '  3. Inv.2: finalizacion de mem_work y memory.events finales\n'
  printf '  4. Inv.3: terminacion del workload y memory.events finales (max/oom/oom_kill)\n'
  printf '  5. Inv.4: baseline de cpu_work (elapsed_s, iterations)\n'
  printf '  6. Inv.4: ejecucion en cpu-half junto con cpu.stat relevante\n'
}

menu() {
  while true; do
    hr
    echo "  LABORATORIO 2 - menu"
    echo "    0) prepare.sh (crear cgroups)"
    echo "    1) Investigacion 1 - PID namespace      [capturas 1 y 2]"
    echo "    2) Investigacion 2 - memory.high         [captura 3]"
    echo "    3) Investigacion 3 - memory.max / OOM    [captura 4]"
    echo "    4) Investigacion 4 - cpu.max / throttling [capturas 5 y 6]"
    echo "    5) reset.sh (limpiar cgroups)"
    echo "    6) correr TODAS las investigaciones en orden"
    echo "    7) resumen de capturas"
    echo "    8) ayuda para grabar/reproducir sesion"
    echo "    q) salir"
    read -r -p "  Opcion: " opt
    case "$opt" in
      0) prepare_lab ;;
      1) inv1 ;;
      2) inv2 ;;
      3) inv3 ;;
      4) inv4 ;;
      5) reset_lab ;;
      6) prepare_lab; inv1; inv2; inv3; inv4; resumen_capturas ;;
      7) resumen_capturas ;;
      8) grabar_help ;;
      q|Q) echo "  chau"; exit 0 ;;
      *) echo "  opcion invalida" ;;
    esac
  done
}

portada
if [ "$#" -ge 1 ]; then
  case "$1" in
    all)    prepare_lab; inv1; inv2; inv3; inv4; resumen_capturas ;;
    prepare) prepare_lab ;;
    inv1)   inv1 ;;
    inv2)   inv2 ;;
    inv3)   inv3 ;;
    inv4)   inv4 ;;
    reset)  reset_lab ;;
    capturas) resumen_capturas ;;
    *)      menu ;;
  esac
else
  menu
fi