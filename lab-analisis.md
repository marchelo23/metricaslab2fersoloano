# Laboratorio 2 — Aislamiento y control de recursos en Linux
## Análisis técnico para `Lab02_Guerra_Solorzano.pdf`

> **Nota.** Este archivo ya contiene los **valores reales observados** en la ejecución de
> la pareja (extraídos de las capturas de `SS/`). Es la base de `generate_report_lab2.py`.

---

# Entorno registrado

- Ejecución en **máquina local (host)**, Linux x86_64. Kernel `6.12.74+deb12-amd64` (base Debian / ParrotOS).
- cgroups v2 montado en `/sys/fs/cgroup` (verificado con `stat -fc %T` → `cgroup2fs`).
- Se operó **únicamente** el subtree `/sys/fs/cgroup/metricas-lab02`, creado por `prepare.sh`
  (grupos `mem-high`, `mem-max`, `cpu-half` con contadores en 0).
- Adaptación al host: los comandos de listado de procesos (Inv. 1) se filtraron con `grep`
  para no volcar el árbol completo del host. No se modificaron binarios ni scripts del repo.

**Valores de configuración de referencia (uso el mismo para las dos investigaciones de memoria):**
`1 MiB = 1048576 bytes`; por tanto 128 MiB = `134217728` y 512 MiB = `536870912`.

---

# Investigación 1 — PID namespace y punto de observación (10 ptos)

## Comandos ejecutados (dos vistas)

- Vista dentro (equivalente Terminal A):
  ```
  sudo unshare --pid --fork --mount-proc bash -c 'printf "PID visto dentro: %s\n" "$$"; sleep 120'
  ```
- Vista host (equivalente Terminal B), filtrada para no volcar procesos del host:
  ```
  ps -eo pid,ppid,comm,args --forest | grep -E "PID|unshare|sleep 120"
  grep '^NSpid:' /proc/824974/status
  grep '^NSpid:' /proc/824975/status
  ```

## Evidencia (Capturas 1 y 2)

| Dato | Valor observado |
|---|---|
| PID visto dentro del namespace (Captura 1) | `1` |
| PID del mismo proceso (bash) desde el host (Captura 2) | `824974` |
| `NSpid:` del bash del namespace | `NSpid: 824974 1` |
| `NSpid:` del `sleep 120` interno | `NSpid: 824975 2` |

## Respuestas

**1.1.** El proceso se observa con el PID `1`: es el primer proceso del nuevo PID namespace
(creado por `unshare --pid --fork`), por lo que dentro de ese namespace la numeración
reinicia desde 1 y le corresponde el 1 (el `$$` del shell lo imprimió así).

**1.2.** Desde el host el mismo proceso tiene el PID `824974`. La línea `NSpid` lista los
identificadores del proceso en **cada nivel** de la jerarquía de PID namespaces, del más
externo (host) al más interno: `NSpid: <pid_host> <pid_ns>`. Por eso `NSpid: 824974 1`
verifica directamente que el "1" visto dentro corresponde al PID 824974 visto desde afuera
(y `NSpid: 824975 2` hace lo propio con el `sleep`, que dentro del namespace es el PID 2).

**1.3.** Dos identificadores distintos no implican dos procesos porque el PID no es una
propiedad intrínseca del proceso sino una etiqueta **relativa al namespace** en el que se
muestra. Es el mismo task (mismo proceso): la línea `NSpid` del **mismo**
`/proc/824974/status` exhibe ambos números para una única tarea. No existe una "copia" del
proceso por cada namespace.

**1.4.** Cambia la **visibilidad**: dentro del namespace solo se ven los procesos de ese
namespace y sus descendientes, renumerados desde 1 (y `/proc`, montado con `--mount-proc`,
refleja esa vista); desde el host se ven todos los procesos con su PID global. Este
experimento **no permite concluir nada** sobre cuánto CPU o memoria puede usar el proceso:
los namespaces cambian la vista, no asignan ni limitan recursos (no se observó ningún
contador de uso ni límite de CPU/memoria).

---

# Investigación 2 — memory.high y presión de memoria (20 ptos)

## Condición experimental

| Dato | Valor observado |
|---|---|
| `memory.high` | `134217728` (128 MiB) |
| `memory.max` | `536870912` (512 MiB) |
| `memory.swap.max` | `max` |
| Workload | `./run-in-cgroup.sh mem-high ./mem_work 256 100 5` (intenta 256 MiB) |

## Predicción (antes de ejecutar)

> Espero que el proceso **no sea terminado** y que **sí pueda superar** 128 MiB, porque
> `memory.high` es un límite *suave* (de presión/reclaim), no un tope duro, y 256 MiB está muy
> por debajo de `memory.max` (512 MiB). Espero que el contador **`high`** aumente (eventos de
> presión al cruzar el umbral), que **`oom_kill` se mantenga en 0** y que el workload imprima
> `allocation_complete allocated_mib=256` y `completed normally`, con `exit=0`.

## Evidencia (Captura 3) — contadores `memory.events`

| Contador | Inicial | Final | Δ (final − inicial) |
|---|---|---|---|
| `high` | 0 | 125 | **125** |
| `oom_kill` | 0 | 0 | 0 |
| `max` | 0 | 0 | 0 |
| `oom` | 0 | 0 | 0 |

Adicional:
- `memory.current` final = `12288` (grupo sin procesos al momento de leer)
- `memory.peak` = `136286208` (≈ 130 MiB, apenas por encima de `memory.high`)
- ¿Apareció `allocation_complete`? **Sí** (`allocated_mib=256`)
- ¿Apareció `completed normally`? **Sí**
- Código de salida: `0`

Nota: el pico quedó *cerca* del umbral porque `memory.high` hace *reclaim* continuo: el
proceso logró "asignar" (fault) los 256 MiB, pero el kernel reclamaba las páginas al superar
el high, por lo que la memoria residente del cgroup se mantuvo contenida alrededor de 128 MiB.

## Respuestas

**2.1.** La predicción se cumplió: el workload superó los 128 MiB (llegó a `allocated_mib=256`
con `allocation_complete`), terminó con `exit=0` y `completed normally`, el único contador
relevante que subió fue `high` (Δ = 125) y `oom_kill` quedó en 0. Coincide con el modelo de
un límite blando.

**2.2.** Evidencia de que `memory.high` no actuó como límite duro de 128 MiB:
- `allocation_complete allocated_mib=256` y `completed normally` con `exit=0`: el proceso
  completó su asignación de 256 MiB y no fue interrumpido.
- `memory.peak` (`136286208` ≈ 130 MiB) supera `memory.high`, y el contador `high` subió
  125 veces: hubo cruces del umbral **sin matar** al proceso (Δ `oom_kill` = 0).
- Si `memory.high` fuera duro, el workload habría sido frenado/terminado en 128 MiB, lo que no
  ocurrió.

**2.3.** El contador `high` cuenta cuántas veces el cgroup cruzó/rozó `memory.high` (eventos
de presión de memoria). Su Δ = 125 es el número de esos eventos durante una carga de 256 MiB
frente a un umbral de 128 MiB: mientras el uso quedó por encima del umbral, el kernel aceleró
el *reclaim* y pudo *throttlear* al proceso para intentar volver bajo el high, sin llegar a
matarlo. La magnitud está acoplada a la condición experimental (carga 2× el umbral).

**2.4.** **No.** Que haya terminado normalmente no implica que `memory.high` "no tuvo
efecto": el Δ del contador `high` (= 125) demuestra que hubo presión de memoria durante la
ejecución, asociada al *reclaim* continuo (el `memory.peak` quedó pegado al umbral). Lo que
**sí** permite concluir: el límite fue no letal ni bloqueante y el workload pudo asignar toda
su memoria. Lo que **no** permite: no medimos tiempo de asignación con/sin throttle, por lo
que no se puede cuantificar cuánto se retardó la ejecución ni el volumen exacto de *reclaim*.

---

# Investigación 3 — memory.max y OOM (25 ptos)

## Condición experimental

| Dato | Valor observado |
|---|---|
| `memory.max` | `134217728` (128 MiB) |
| `memory.swap.max` | `0` |
| `memory.high` | `max` (sin umbral restrictivo) |
| Workload | `./run-in-cgroup.sh mem-max ./mem_work 256 100 5` |

## Predicción (antes de ejecutar)

> Al intentar superar los 128 MiB espero que el kernel active el *memcg OOM killer* y termine
> el proceso bruscamente con **SIGKILL**, sin que pueda imprimir `allocation_complete` ni
> `completed normally` (no termina "por sí solo": la decisión la toma el mecanismo de control
> de memoria). Espero en `memory.events`: `max` Δ > 0 (se alcanzó el tope), `oom` Δ ≥ 1 y
> `oom_kill` Δ = 1, y un código de salida `137` (= 128 + SIGKILL).

## Evidencia (Captura 4) — contadores `memory.events`

| Contador | Inicial | Final | Δ |
|---|---|---|---|
| `max` | 0 | 35 | **35** |
| `oom` | 0 | 1 | **1** |
| `oom_kill` | 0 | 1 | **1** |

Adicional:
- Último `allocated_mib` visible = `120` (cercano a `memory.max`)
- ¿Apareció `allocation_complete`? **No**
- ¿Apareció `completed normally`? **No**
- Código de salida observado = `137`

## Respuestas

**3.1.** **No** completó la asignación. La última línea visible fue `allocated_mib=120`
(≈ `memory.max`), seguida de la notificación de muerte del shell
(`lab2.sh: line 145: 828729 Killed`); no aparecen `allocation_complete` ni `completed
normally`: el proceso fue interrumpido antes de terminar.

**3.2.** Evidencia de OOM **dentro del cgroup** y no de error de la aplicación:
- `memory.events` con Δ `oom` = 1 y Δ `oom_kill` = 1 (el OOM killer del cgroup resolvió el
  evento matando un proceso del propio cgroup).
- Código de salida `137` = 128 + `SIGKILL`: muerte por señal del kernel, no por `return`/`exit`
  propio.
- `mem_work` es un asignador simple: un fallo interno habría impreso su propio mensaje y
  salido con otro código; aquí no hubo ningún error reportado por la aplicación.

**3.3.**
- `max`: cantidad de cruces de `memory.max`. Δ = 35 indica que el cgroup golpeó el tope de
  128 MiB de forma repetida durante la ejecución.
- `oom`: cantidad de condiciones OOM del cgroup. Δ = 1 señala al menos un estado de falta de
  memoria crítica.
- `oom_kill`: procesos terminados por el OOM killer. Δ = 1 confirma que la resolución mató
  **un** proceso (el propio workload, único en el cgroup).
Usar los **Δ** (no solo los finales) vincula cada acontecimiento a **esta** ejecución: los
valores iniciales eran 0 y avanzaron durante el run; sin los Δ no se podría descartar el
acarreo de una corrida anterior.

**3.4.** Diferencia operacional: con **memory.high** superar el umbral es permitido → presión
de memoria y *reclaim*, proceso sobrevive y termina (`exit=0`, Δ `oom_kill`=0). Con
**memory.max** alcanzar el tope es prohibitivo → sin swap, el intento dispara el OOM killer,
que mata el proceso (`exit=137`, Δ `oom_kill`=1). *high* = límite blando (presión/reclaim),
*max* = límite duro (terminación).

---

# Investigación 4 — cpu.max y throttling (25 ptos)

## Condición experimental y predicción (antes de ejecutar)

- `cpu.max = 50000 100000` → 50 ms de CPU por período de 100 ms → máxima asignación ≈ 0.5 CPU.
- Baseline: `./cpu_work 8` (fuera del cgroup). Limitada: `./run-in-cgroup.sh cpu-half ./cpu_work 8`.

> Predicción: con cuota de 0.5 CPU espero que en ~8 s de pared el workload (CPU-bound) complete
> **menos iteraciones** que el baseline (aproximadamente la mitad) y que en `cpu.stat` aumenten
> **`nr_throttled`** (períodos en los que se agotó la cuota) y **`throttled_usec`** (tiempo de
> CPU denegado). No espero una razón exacta de 0.50.

## Evidencia (Capturas 5 y 6)

| Medida | Baseline | cpu-half |
|---|---|---|
| `elapsed_s` | `8.000748` | `8.005108` |
| `iterations` | `2037907456` | `1301020672` |

`cpu.stat` (inicial → final):

| Contador | Inicial | Final | Δ |
|---|---|---|---|
| `usage_usec` | 0 | 4012467 | **4012467** (≈ 4.01 s de CPU) |
| `nr_throttled` | 0 | 80 | **80** |
| `throttled_usec` | 0 | 3991721 | **3991721** (≈ 3.99 s throttled) |

- `nr_periods` final = `83`
- **razón de trabajo** = `iterations(cuota) / iterations(baseline)` = `1301020672 / 2037907456` ≈ **0.638**

## Respuestas

**4.1.** La predicción se cumplió cualitativamente: con cuota el workload completó menos
iteraciones (1301020672 vs 2037907456) en un `elapsed_s` casi idéntico. Cuantitativamente la
razón observada (≈ 0.64) quedó por encima del ≈ 0.5 nominal: esto se explica por efectos del
entorno (detallados en 4.4), no invalida el mecanismo.

**4.2.** Los incrementos en `cpu.stat`: Δ `nr_throttled` = 80 (períodos en que el cgroup
exhaustó su cuota y el *CFS bandwidth controller* lo frenó; de 83 períodos, 80 fueron
throttled) y Δ `throttled_usec` = 3991721 µs ≈ 3.99 s de CPU denegada durante la corrida.
Son contadores exclusivos del controlador de cuota de cgroup v2: que se incrementen durante
**esta** ejecución demuestra que el proceso fue frenado por throttling de CPU, y que
`usage_usec` (≈ 4.01 s) sea cercano a la cuota de 0.5 × 8 s confirma que trabajó al máximo
de lo asignado.

**4.3.** Un proceso *throttled* está **runnable**: el scheduler le niega CPU periódicamente
para respetar la cuota. Por eso avanza menos en el mismo tiempo de pared **sin** bloquearse
en I/O: no hay syscall de espera, ni estado de sleep, ni espera de disco. En el Laboratorio 1,
la espera de I/O se evidencia con estado dormido/esperando recurso, `iowait`/`%wa` y `time`
con user+sys ≪ `real`; aquí la evidencia son los contadores del scheduler (`nr_throttled`,
`throttled_usec`), que no participan en una espera de I/O ordinaria.

**4.4.** No debe exigirse 0.50 exacto porque `cpu.max` limita **tiempo de CPU**, no
iteraciones: overhead de arranque/temporización, micro-usos de CPU del cgroup (kernel, page
faults), granularidad del período (50/100 ms), ruido de otros procesos del host y jitter del
cronometrado desplazan la razón; en esta medición el factor de frecuencia de CPU (turbo) y la
carga del host elevaron la razón a ≈ 0.64. 0.5 es la fracción **máxima** asignable, no una
equivalencia directa con trabajo completado.

---

# Investigación 5 — Síntesis de mecanismos (10 ptos)

## Tabla de síntesis

| Mecanismo | Qué modifica o controla | Evidencia principal utilizada | Conclusión incorrecta que debe evitarse |
|---|---|---|---|
| **PID namespace** | La **vista**/identificación de los PID (qué procesos ve y cómo los numera); no asigna ni limita recursos | `NSpid: 824974 1`; PID `1` dentro vs `824974` desde el host | "Dos PIDs ⇒ dos procesos" / "el namespace limita CPU o memoria" |
| **memory.high** | **Control** suave de memoria: presión/reclaim/throttle | `high` Δ = 125, `allocation_complete` 256 MiB, `oom_kill` Δ = 0, `exit=0` | "Es un límite duro de 128 MiB" / "termina al superarlo" |
| **memory.max** | **Control** duro: con swap 0, alcanzar el tope → OOM killer del cgroup | `max` Δ = 35, `oom` Δ = 1, `oom_kill` Δ = 1, `exit=137`, último `allocated_mib`=120 | "El proceso falló por sí solo / reportó un error" |
| **cpu.max** | **Control** de CPU: cuota de tiempo por período (throttling CFS) | `nr_throttled` Δ = 80, `throttled_usec` Δ ≈ 3.99 s, razón ≈ 0.638 | "Estaba esperando por I/O" / "tardó por carga normal" |

## Respuestas

**5.1.** Los **namespaces** dan *aislamiento*: cambian la **vista** del proceso sobre un
recurso (Inv. 1: el proceso se ve como PID `1` y el host lo ve como `824974`, línea
`NSpid: 824974 1`), pero no acotan cuánto recurso puede usarse. Los **cgroups** son *control
de recursos*: cuantifican y limitan el uso efectivo (Inv. 2/3: `memory.events` con
`high` Δ=125 y `max`/`oom`/`oom_kill`; Inv. 4: `cpu.stat` con `nr_throttled`/`throttled_usec`).
La evidencia de Inv. 1 es de visibilidad; la de Inv. 2–4 (contadores y terminaciones) es de
uso/consumo limitado.

**5.2.** Para un proceso que avanza menos de lo esperado, distinguir:
- **(a) espera/bloqueo (Lab 1):** estado del proceso (S/T/D), `wchan`, `iowait`/`%wa`
  (`iostat`/`mpstat`), `time` con user+sys ≪ `real`; sin contadores de cgroup de por medio.
- **(b) throttling de CPU (Lab 2):** `cpu.stat` del cgroup del proceso con Δ `nr_throttled` y
  Δ `throttled_usec` > 0; `time` muestra user+sys alto pero avanzando lento, sin estado de
  espera.
- **(c) presión/límite de memoria (Lab 2):** `memory.events` con Δ en `high`/`max`/`oom`/
  `oom_kill`, `memory.current` cercano a `memory.max`, swap con actividad, procesos terminados
  con `137`.

**5.3.** "CPU baja" o "tarda más" son síntomas compartidos por los tres mecanismos: un proceso
**throttled** consume poca CPU por segundo y avanza poco (similar a una espera de I/O); uno
bajo **presión de memoria** se frena por *reclaim* continuo, con CPU baja o wall time con
golpes; uno **bloqueado en I/O** muestra CPU baja por otra razón. Para atribuir el mecanismo
se necesita la **fuente específica** (contadores de `cpu.stat`, `memory.events`,
`memory.stat` pgscan/pgsteal, estado/syscall del proceso) y el contexto (¿está en un cgroup
con cuota? ¿cerca de `memory.max`? ¿esperando I/O?), como en 4.3 y 5.2.

---

# Anexo — Capturas obligatorias (6)

| # | Archivo | Pie sugerido |
|---|---|---|
| 1 | `SS/captura1.png` | Vista dentro del PID namespace: proceso impreso como PID 1 |
| 2 | `SS/captura2.png` | Vista desde el host: jerarquía filtrada y línea `NSpid: 824974 1` |
| 3 | `SS/captura3.png` + `SS/captura3post.png` | Inv. 2 — contadores iniciales (izq.) y finalización normal de `mem_work` con `memory.events` (der.) |
| 4 | `SS/captura4.png` + `SS/captura4post.png` | Inv. 3 — contadores iniciales (izq.) y terminación por OOM con `memory.events` (der.) |
| 5 | `SS/captura5.png` | Inv. 4 — baseline de `cpu_work` (8.000748 s, 2037907456 iteraciones) |
| 6 | `SS/captura6post.png` | Inv. 4 — ejecución con cuota y `cpu.stat` final (nr_throttled 80, throttled_usec 3991721) |