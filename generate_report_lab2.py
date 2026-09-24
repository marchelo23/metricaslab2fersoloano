#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Genera Lab02_Guerra_Solorzano.pdf a partir del informe HTML (estilo Lab01).
import os
import subprocess

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(LAB_DIR, "informe_completo_lab2.html")
PDF_PATH = os.path.join(LAB_DIR, "Lab02_Guerra_Solorzano.pdf")

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Laboratorio 2 - Aislamiento y control de recursos en Linux</title>
<style>
    @page {
        size: letter;
        margin: 14mm 14mm 14mm 14mm;
        @bottom-right {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 8pt;
            color: #666;
            font-family: sans-serif;
        }
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #1a1a1a;
        line-height: 1.38;
        font-size: 9.4pt;
        margin: 0;
        padding: 0;
    }
    .header {
        border-bottom: 2.5px solid #003366;
        padding-bottom: 5px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .header-left h1 {
        font-size: 14.5pt;
        color: #003366;
        margin: 0 0 2px 0;
        font-weight: 800;
        letter-spacing: -0.3px;
    }
    .header-left h2 {
        font-size: 10pt;
        color: #444;
        margin: 0;
        font-weight: 500;
    }
    .header-right {
        text-align: right;
        font-size: 8.5pt;
        color: #555;
    }
    .authors-card {
        background: #f0f4f8;
        border-left: 4px solid #003366;
        padding: 6px 12px;
        margin-bottom: 12px;
        border-radius: 0 4px 4px 0;
        font-size: 9pt;
    }
    .authors-card strong {
        color: #003366;
    }
    h2.section-title {
        font-size: 11.5pt;
        color: #003366;
        border-bottom: 1.5px solid #dcdcdc;
        padding-bottom: 2px;
        margin-top: 12px;
        margin-bottom: 8px;
        page-break-after: avoid;
        font-weight: 700;
    }
    h3.question-title {
        font-size: 9.4pt;
        color: #111;
        margin-top: 8px;
        margin-bottom: 4px;
        page-break-after: avoid;
        font-weight: 600;
    }
    p { margin: 0 0 5px 0; text-align: justify; }
    ul { margin: 2px 0 5px 16px; padding: 0; }
    li { margin-bottom: 2px; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 5px 0 8px 0;
        font-size: 8.6pt;
        page-break-inside: avoid;
    }
    th, td {
        border: 1px solid #c8d1dc;
        padding: 3.5px 7px;
        text-align: left;
    }
    th { background-color: #e9eef4; color: #003366; font-weight: 600; }
    tr:nth-child(even) td { background-color: #fbfcfd; }
    .figure-container {
        margin: 8px 0 10px 0;
        text-align: center;
        page-break-inside: avoid;
    }
    .figure-container img.standard-img {
        max-width: 95%;
        height: auto;
        border: 1px solid #777;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        display: block;
        margin: 0 auto;
    }
    .figure-container img.large-img {
        width: 100%;
        max-width: 100%;
        height: auto;
        border: 1.5px solid #444;
        border-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
        display: block;
        margin: 0 auto;
    }
    .figure-pair {
        display: flex;
        gap: 8px;
        justify-content: center;
        align-items: flex-start;
        margin-bottom: 4px;
    }
    .figure-pair figure {
        flex: 1 1 50%;
        margin: 0;
        min-width: 0;
    }
    .figure-pair img {
        width: 100%;
        height: auto;
        border: 1px solid #777;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .caption {
        font-size: 8.2pt;
        color: #333;
        margin-top: 4px;
        font-style: italic;
    }
    .caption strong { color: #003366; font-style: normal; }
    .code-box {
        background-color: #222;
        color: #f1f1f1;
        font-family: 'Consolas', 'Courier New', monospace;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 8pt;
        line-height: 1.25;
        margin: 4px 0 6px 0;
        white-space: pre-wrap;
    }
    .pred-box {
        background: #fdf6e3;
        border-left: 4px solid #b06000;
        padding: 6px 10px;
        margin: 4px 0 8px 0;
        border-radius: 0 4px 4px 0;
        font-size: 8.9pt;
        page-break-inside: avoid;
    }
    .pred-box strong { color: #b06000; }
    .page-break { page-break-before: always; }
    .highlight {
        background-color: #e8f0fe;
        color: #174ea6;
        padding: 1px 3px;
        border-radius: 3px;
        font-family: 'Consolas', monospace;
        font-size: 8.3pt;
    }
</style>
</head>
<body>

<div class="header">
    <div class="header-left">
        <h1>Laboratorio 2</h1>
        <h2>Aislamiento y control de recursos en Linux</h2>
    </div>
    <div class="header-right">
        <strong>Métricas de Software</strong><br>
        Ciclo III 2026 · ESEN
    </div>
</div>

<div class="authors-card">
    <strong>Estudiantes (Pareja):</strong> Guerra y Solórzano &nbsp;&nbsp;|&nbsp;&nbsp;
    <strong>Docente:</strong> Guillermo Calderón &nbsp;&nbsp;|&nbsp;&nbsp;
    <strong>Entorno:</strong> ParrotOS (host local) · Linux x86_64 · cgroups v2
</div>

<h2 class="section-title">Investigación 1. PID namespace y punto de observación (10 puntos)</h2>
<p><strong>Pregunta:</strong> Determinar cómo cambia el identificador visible de un proceso cuando se observa desde un PID namespace y desde el host.</p>

<p><strong>Comandos ejecutados (dos vistas):</strong></p>
<div class="code-box"># Vista dentro (equiv. Terminal A)
sudo unshare --pid --fork --mount-proc bash -c 'printf "PID visto dentro: %s\n" "$$"; sleep 120'

# Vista host (equiv. Terminal B) - filtrada para no volcar los procesos del host
ps -eo pid,ppid,comm,args --forest | grep -E "PID|unshare|sleep 120"
grep '^NSpid:' /proc/824974/status
grep '^NSpid:' /proc/824975/status</div>

<p><strong>Tabla de evidencia observada:</strong></p>
<table>
    <thead>
        <tr><th>Dato</th><th>Valor observado</th><th>Fuente</th></tr>
    </thead>
    <tbody>
        <tr><td>PID visto dentro del namespace (Captura 1)</td><td><code>1</code></td><td>salida del shell dentro del namespace ($$)</td></tr>
        <tr><td>PID del mismo proceso (bash) desde el host</td><td><code>824974</code></td><td><code>ps --forest</code> filtrado</td></tr>
        <tr><td><code>NSpid:</code> del bash del namespace</td><td><code>NSpid: 824974 1</code></td><td><code>/proc/824974/status</code></td></tr>
        <tr><td><code>NSpid:</code> del <code>sleep 120</code> interno</td><td><code>NSpid: 824975 2</code></td><td><code>/proc/824975/status</code></td></tr>
    </tbody>
</table>

<div class="figure-container">
    <img class="standard-img" src="SS/captura1.png" alt="Captura obligatoria 1">
    <div class="caption"><strong>Captura obligatoria 1:</strong> Vista dentro del PID namespace: el proceso se imprime como PID 1.</div>
</div>

<div class="figure-container">
    <img class="standard-img" src="SS/captura2.png" alt="Captura obligatoria 2">
    <div class="caption"><strong>Captura obligatoria 2:</strong> Vista desde el host: jerarquía filtrada del unshare/bash/sleep y líneas <code>NSpid</code> de los procesos 824974 y 824975.</div>
</div>

<h3 class="question-title">1.1. ¿Qué PID observa el proceso desde dentro del namespace?</h3>
<p>El PID <code>1</code>: es el primer proceso del nuevo PID namespace creado por <code>unshare --pid --fork</code>, por lo que la numeración reinicia desde 1 y le corresponde el 1 (así lo imprimió el <code>$$</code> del shell).</p>

<h3 class="question-title">1.2. ¿Qué PID corresponde al mismo proceso desde el host? Interprete la línea NSpid.</h3>
<p>Desde el host, el mismo proceso tiene el PID <code>824974</code>. La línea <span class="highlight">NSpid</span> lista los identificadores del proceso en <strong>cada nivel</strong> de la jerarquía de PID namespaces, del más externo (host) al más interno: <code>NSpid: &lt;pid_host&gt; &lt;pid_ns&gt;</code>. Así, <code>NSpid: 824974 1</code> verifica que el "1" visto dentro corresponde al PID 824974 observado desde el host; <code>NSpid: 824975 2</code> hace lo propio con el <code>sleep</code> (PID 2 dentro del namespace).</p>

<h3 class="question-title">1.3. ¿Por qué dos identificadores distintos no implican dos procesos independientes?</h3>
<p>Porque el PID no es una propiedad intrínseca del proceso sino una etiqueta <strong>relativa al namespace</strong> en el que se muestra. Es el mismo task: la línea <code>NSpid</code> del <strong>mismo</strong> <code>/proc/824974/status</code> exhibe ambos números para una única tarea, sin que exista ninguna "copia" por namespace.</p>

<h3 class="question-title">1.4. ¿Qué cambia en la visibilidad de los PID? ¿Qué no permite concluir este experimento sobre CPU y memoria?</h3>
<p>Cambia la <strong>visibilidad</strong>: dentro del namespace solo se ven los procesos de ese namespace y sus descendientes, renumerados desde 1 (con <code>--mount-proc</code>, <code>/proc</code> refleja esa vista); desde el host se ven todos los procesos con su PID global. Este experimento <strong>no permite concluir nada</strong> sobre cuánto CPU o memoria puede usar el proceso: los namespaces cambian la vista, no asignan ni limitan recursos (no se observó ningún contador de uso ni límite).</p>

<div class="page-break"></div>
<h2 class="section-title">Investigación 2. memory.high y presión de memoria (20 puntos)</h2>
<p><strong>Condición experimental:</strong> grupo <code>mem-high</code> con <code>memory.high=128 MiB</code> y <code>memory.max=512 MiB</code>; el workload intenta 256 MiB.</p>
<table>
    <thead><tr><th>Dato</th><th>Valor observado</th></tr></thead>
    <tbody>
        <tr><td><code>memory.high</code></td><td><code>134217728</code> (128 MiB)</td></tr>
        <tr><td><code>memory.max</code></td><td><code>536870912</code> (512 MiB)</td></tr>
        <tr><td>Workload</td><td><code>./run-in-cgroup.sh mem-high ./mem_work 256 100 5</code></td></tr>
    </tbody>
</table>

<div class="pred-box"><strong>Predicción:</strong> espero que el proceso <strong>no sea terminado</strong> y que <strong>sí pueda superar</strong> 128 MiB, porque <code>memory.high</code> es un límite <em>suave</em> (de presión/reclaim), no un tope duro, y 256 MiB está muy por debajo de <code>memory.max</code> (512 MiB). Espero que el contador <strong><code>high</code></strong> aumente (eventos de presión al cruzar el umbral), que <strong><code>oom_kill</code> se mantenga en 0</strong> y que el workload imprima <code>allocation_complete allocated_mib=256</code> y <code>completed normally</code>, con <code>exit=0</code>.</div>

<p><strong>Evidencia (Captura 3) — contadores <code>memory.events</code>:</strong></p>
<table>
    <thead><tr><th>Contador</th><th>Inicial</th><th>Final</th><th>Δ (final − inicial)</th></tr></thead>
    <tbody>
        <tr><td><code>high</code></td><td>0</td><td>125</td><td><strong>125</strong></td></tr>
        <tr><td><code>max</code></td><td>0</td><td>0</td><td>0</td></tr>
        <tr><td><code>oom</code></td><td>0</td><td>0</td><td>0</td></tr>
        <tr><td><code>oom_kill</code></td><td>0</td><td>0</td><td>0</td></tr>
    </tbody>
</table>

<p><strong>Datos adicionales:</strong></p>
<table>
    <thead><tr><th>Dato</th><th>Valor observado</th></tr></thead>
    <tbody>
        <tr><td><code>memory.current</code> final</td><td><code>12288</code> (grupo sin procesos al leer)</td></tr>
        <tr><td><code>memory.peak</code></td><td><code>136286208</code> (≈ 130 MiB, apenas sobre <code>memory.high</code>)</td></tr>
        <tr><td>¿Apareció <code>allocation_complete</code>?</td><td><strong>Sí</strong> (<code>allocated_mib=256</code>)</td></tr>
        <tr><td>¿Apareció <code>completed normally</code>?</td><td><strong>Sí</strong></td></tr>
        <tr><td>Código de salida</td><td><code>0</code></td></tr>
    </tbody>
</table>
<p>Nota: el pico quedó <em>cerca</em> del umbral porque <code>memory.high</code> hace <em>reclaim</em> continuo: el proceso logró "asignar" (fault) los 256 MiB, pero al superar el high el kernel reclamaba páginas, manteniendo la memoria residente del cgroup alrededor de 128 MiB.</p>

<div class="figure-container">
    <div class="figure-pair">
        <figure><img src="SS/captura3.png" alt="Contadores iniciales Inv.2"></figure>
        <figure><img src="SS/captura3post.png" alt="Finalización Inv.2"></figure>
    </div>
    <div class="caption"><strong>Captura obligatoria 3:</strong> Inicial (izq.): configuración y contadores de <code>mem-high</code>. Final (der.): terminación normal de <code>mem_work</code> (<code>allocation_complete</code>, <code>completed normally</code>, <code>exit=0</code>) y <code>memory.events</code> con <code>high 125</code> y <code>oom_kill 0</code>.</div>
</div>

<h3 class="question-title">2.1. Contraste la predicción con el resultado observado.</h3>
<p>La predicción se cumplió: el workload superó los 128 MiB (llegó a <code>allocated_mib=256</code> con <code>allocation_complete</code>), terminó con <code>exit=0</code> y <code>completed normally</code>; el único contador relevante que subió fue <code>high</code> (Δ = 125) y <code>oom_kill</code> quedó en 0. Comportamiento típico de un límite blando.</p>

<h3 class="question-title">2.2. ¿Qué evidencia permite afirmar que memory.high no actuó como un límite duro de 128 MiB?</h3>
<ul>
    <li><code>allocation_complete allocated_mib=256</code> y <code>completed normally</code> con <code>exit=0</code>: el proceso completó su asignación y no fue interrumpido.</li>
    <li><code>memory.peak</code> (<code>136286208</code> ≈ 130 MiB) supera <code>memory.high</code> y además el contador <code>high</code> subió 125 veces: hubo cruces del umbral <strong>sin matar</strong> al proceso (Δ <code>oom_kill</code> = 0). Un límite duro habría frenado o terminado el proceso en 128 MiB.</li>
</ul>

<h3 class="question-title">2.3. ¿Qué significado tiene el incremento en el contador high? Relaciónelo con la condición experimental.</h3>
<p>El contador <code>high</code> cuenta cuántas veces el cgroup cruzó/rozó <code>memory.high</code> (eventos de presión de memoria). Su Δ = 125 es el número de eventos durante una carga de 256 MiB frente a un umbral de 128 MiB: mientras el uso quedó por encima del umbral, el kernel aceleró el <em>reclaim</em> y pudo <em>throttlear</em> al proceso, sin matarlo. La magnitud está acoplada a la condición experimental (carga ≈ 2× el umbral).</p>

<h3 class="question-title">2.4. ¿Puede concluirse, solo porque terminó normalmente, que memory.high no tuvo efecto?</h3>
<p><strong>No.</strong> Que haya terminado normalmente no implica "sin efecto": el Δ de <code>high</code> (= 125) demuestra que hubo presión de memoria, asociada al <em>reclaim</em> continuo (<code>memory.peak</code> quedó pegado al umbral). Lo que <strong>sí</strong> permite concluir es que el límite fue no letal ni bloqueante y que el workload pudo asignar toda su memoria. Lo que <strong>no</strong> permite: cuantificar cuánto se retardó la ejecución (throttle) ni el volumen exacto de <em>reclaim</em>, porque no se midió tiempo de asignación con/sin throttle.</p>

<div class="page-break"></div>
<h2 class="section-title">Investigación 3. memory.max y OOM (25 puntos)</h2>
<p><strong>Condición experimental:</strong> grupo <code>mem-max</code> con <code>memory.max=128 MiB</code>, <code>memory.swap.max=0</code> y sin umbral restrictivo en <code>memory.high</code>; el workload vuelve a intentar 256 MiB.</p>
<table>
    <thead><tr><th>Dato</th><th>Valor observado</th></tr></thead>
    <tbody>
        <tr><td><code>memory.max</code></td><td><code>134217728</code> (128 MiB)</td></tr>
        <tr><td><code>memory.swap.max</code></td><td><code>0</code></td></tr>
        <tr><td><code>memory.high</code></td><td><code>max</code></td></tr>
    </tbody>
</table>

<div class="pred-box"><strong>Predicción:</strong> al intentar superar los 128 MiB espero que el kernel active el <em>memcg OOM killer</em> y termine el proceso bruscamente con <strong>SIGKILL</strong>, sin que pueda imprimir <code>allocation_complete</code> ni <code>completed normally</code> (no termina "por sí solo": la decisión la toma el mecanismo de control de memoria). Espero en <code>memory.events</code>: <code>max</code> Δ &gt; 0, <code>oom</code> Δ ≥ 1 y <code>oom_kill</code> Δ = 1, con código de salida <code>137</code> (= 128 + SIGKILL).</div>

<p><strong>Evidencia (Captura 4) — contadores <code>memory.events</code>:</strong></p>
<table>
    <thead><tr><th>Contador</th><th>Inicial</th><th>Final</th><th>Δ</th></tr></thead>
    <tbody>
        <tr><td><code>max</code></td><td>0</td><td>35</td><td><strong>35</strong></td></tr>
        <tr><td><code>oom</code></td><td>0</td><td>1</td><td><strong>1</strong></td></tr>
        <tr><td><code>oom_kill</code></td><td>0</td><td>1</td><td><strong>1</strong></td></tr>
    </tbody>
</table>

<p><strong>Datos adicionales:</strong></p>
<table>
    <thead><tr><th>Dato</th><th>Valor observado</th></tr></thead>
    <tbody>
        <tr><td><code>memory.max</code></td><td><code>134217728</code> (128 MiB)</td></tr>
        <tr><td><code>memory.swap.max</code></td><td><code>0</code></td></tr>
        <tr><td>Último <code>allocated_mib</code> visible</td><td><code>120</code></td></tr>
        <tr><td>¿Apareció <code>allocation_complete</code>?</td><td><strong>No</strong></td></tr>
        <tr><td>¿Apareció <code>completed normally</code>?</td><td><strong>No</strong></td></tr>
        <tr><td>Código de salida observado</td><td><code>137</code></td></tr>
    </tbody>
</table>

<div class="figure-container">
    <div class="figure-pair">
        <figure><img src="SS/captura4.png" alt="Contadores iniciales + ejecución Inv.3"></figure>
        <figure><img src="SS/captura4post.png" alt="Terminación OOM Inv.3"></figure>
    </div>
    <div class="caption"><strong>Captura obligatoria 4:</strong> Inicial (izq.): configuración, contadores en 0 y comienzo de la ejecución. Final (der.): terminación por OOM (proceso <code>Killed</code>, <code>exit=137</code>) y <code>memory.events</code> final con <code>max 35</code>, <code>oom 1</code>, <code>oom_kill 1</code>.</div>
</div>

<h3 class="question-title">3.1. ¿Completó el workload la asignación de 256 MiB? Sustente.</h3>
<p><strong>No.</strong> La última línea visible fue <code>allocated_mib=120</code> (≈ <code>memory.max</code>), seguida de la notificación de muerte del shell (<code>lab2.sh: line 145: 828729 Killed</code>); no aparecen <code>allocation_complete</code> ni <code>completed normally</code>: el proceso fue interrumpido antes de terminar.</p>

<h3 class="question-title">3.2. ¿Qué evidencia atribuye la terminación a un OOM del cgroup y no a un error de la aplicación?</h3>
<ul>
    <li><code>memory.events</code> con Δ <code>oom</code> = 1 y Δ <code>oom_kill</code> = 1: el OOM killer del cgroup resolvió el evento matando un proceso del propio cgroup.</li>
    <li>Código de salida <code>137</code> = 128 + <code>SIGKILL</code>: muerte por señal del kernel, no por <code>return</code>/<code>exit</code> propio.</li>
    <li><code>mem_work</code> es un asignador simple: un fallo interno habría impreso su propio mensaje y salido con otro código; aquí la app no reportó ningún error.</li>
</ul>

<h3 class="question-title">3.3. Función de max, oom y oom_kill. Use sus incrementos.</h3>
<p><code>max</code> cuenta los cruces de <code>memory.max</code>: su Δ = 35 indica que el cgroup golpeó el tope de 128 MiB de forma repetida. <code>oom</code> cuenta las condiciones OOM del cgroup: su Δ = 1 señala al menos un estado de falta de memoria crítica. <code>oom_kill</code> cuenta procesos terminados por el OOM killer: su Δ = 1 confirma que se mató <strong>un</strong> proceso (el propio workload, único en el cgroup). Usar los <strong>Δ</strong> (no solo los finales) vincula cada suceso a <strong>esta</strong> ejecución: iniciales en 0 que avanzaron durante el run.</p>

<h3 class="question-title">3.4. Compare con la Investigación 2.</h3>
<p>Con <strong>memory.high</strong>, superar el umbral es permitido: presión y <em>reclaim</em>, el proceso sobrevive y termina (<code>exit=0</code>, Δ <code>oom_kill</code>=0). Con <strong>memory.max</strong>, alcanzar el tope es prohibitivo: sin swap, dispara el OOM killer, que mata el proceso (<code>exit=137</code>, Δ <code>oom_kill</code>=1). <em>high</em> = límite blando (presión/reclaim); <em>max</em> = límite duro (terminación).</p>

<div class="page-break"></div>
<h2 class="section-title">Investigación 4. cpu.max y throttling (25 puntos)</h2>
<p><strong>Condición:</strong> <code>cpu-half</code> con <code>cpu.max = 50000 100000</code> (50 ms de CPU por período de 100 ms ≈ 0.5 CPU). Baseline: <code>./cpu_work 8</code> fuera del cgroup.</p>

<div class="pred-box"><strong>Predicción:</strong> con cuota de 0.5 CPU espero que en ~8 s de pared el workload (CPU-bound) complete <strong>menos iteraciones</strong> que el baseline (aproximadamente la mitad) y que en <code>cpu.stat</code> aumenten <strong><code>nr_throttled</code></strong> (períodos en que se agotó la cuota) y <strong><code>throttled_usec</code></strong> (tiempo de CPU denegado). No espero una razón exacta de 0.50.</div>

<p><strong>Evidencia (Capturas 5 y 6):</strong></p>
<table>
    <thead><tr><th>Medida</th><th>Baseline</th><th>cpu-half</th></tr></thead>
    <tbody>
        <tr><td><code>elapsed_s</code></td><td><code>8.000748</code></td><td><code>8.005108</code></td></tr>
        <tr><td><code>iterations</code></td><td><code>2037907456</code></td><td><code>1301020672</code></td></tr>
    </tbody>
</table>

<p><strong><code>cpu.stat</code> del cgroup (inicial → final):</strong></p>
<table>
    <thead><tr><th>Contador</th><th>Inicial</th><th>Final</th><th>Δ</th></tr></thead>
    <tbody>
        <tr><td><code>usage_usec</code></td><td>0</td><td>4012467</td><td><strong>4012467</strong> (≈ 4.01 s de CPU)</td></tr>
        <tr><td><code>nr_throttled</code></td><td>0</td><td>80</td><td><strong>80</strong></td></tr>
        <tr><td><code>throttled_usec</code></td><td>0</td><td>3991721</td><td><strong>3991721</strong> (≈ 3.99 s throttled)</td></tr>
    </tbody>
</table>
<p><code>nr_periods</code> final = <code>83</code>. <strong>razón de trabajo</strong> = <code>1301020672 / 2037907456</code> ≈ <strong>0.638</strong>.</p>

<div class="figure-container">
    <img class="large-img" src="SS/captura5.png" alt="Captura obligatoria 5">
    <div class="caption"><strong>Captura obligatoria 5:</strong> Baseline fuera del cgroup: <code>elapsed_s=8.000748</code>, <code>iterations=2037907456</code>.</div>
</div>

<div class="figure-container">
    <img class="large-img" src="SS/captura6post.png" alt="Captura obligatoria 6">
    <div class="caption"><strong>Captura obligatoria 6:</strong> Ejecución con cuota (<code>elapsed_s=8.005108</code>, <code>iterations=1301020672</code>) y <code>cpu.stat</code> final con <code>nr_throttled 80</code> y <code>throttled_usec 3991721</code>.</div>
</div>

<h3 class="question-title">4.1. Contraste la predicción con las iteraciones observadas.</h3>
<p>La predicción se cumplió cualitativamente: con cuota, el workload completó menos iteraciones (1301020672 vs 2037907456) en un <code>elapsed_s</code> casi idéntico. Cuantitativamente la razón (≈ 0.64) quedó por encima del ≈ 0.5 nominal, lo que se explica por efectos del entorno (detallados en 4.4) y no invalida el mecanismo.</p>

<h3 class="question-title">4.2. ¿Qué evidencia de cpu.stat permite afirmar el throttling? Sustente con los Δ.</h3>
<p>Los incrementos en <code>cpu.stat</code>: Δ <code>nr_throttled</code> = 80 (de 83 períodos, 80 fueron throttled: el cgroup exhaustó su cuota y el <em>CFS bandwidth controller</em> lo frenó) y Δ <code>throttled_usec</code> = 3991721 µs ≈ 3.99 s de CPU denegada. Son contadores exclusivos del controlador de cuota de cgroup v2: que se incrementen durante <strong>esta</strong> ejecución demuestra el throttling, y <code>usage_usec</code> (≈ 4.01 s) cercano a la cuota (0.5 × 8 s) confirma que trabajó al máximo de lo asignado.</p>

<h3 class="question-title">4.3. ¿Por qué menos iteraciones en el mismo tiempo no es espera de I/O (Lab 1)?</h3>
<p>Un proceso <em>throttled</em> está <strong>runnable</strong>: el scheduler le niega CPU periódicamente para respetar la cuota. Avanza menos en el mismo tiempo de pared <strong>sin</strong> bloquearse en I/O: no hay syscall de espera, ni estado de sleep, ni espera de disco. En el Lab 1, la espera de I/O se evidencia con estado dormido/esperando recurso, <code>iowait</code>/<code>%wa</code> y <code>time</code> con user+sys ≪ <code>real</code>; aquí la evidencia son los contadores del scheduler (<code>nr_throttled</code>, <code>throttled_usec</code>), que no participan en una espera de I/O ordinaria.</p>

<h3 class="question-title">4.4. ¿Por qué no exigir razón exactamente 0.50?</h3>
<p><code>cpu.max</code> limita <strong>tiempo de CPU</strong>, no iteraciones; overhead de arranque/temporización, micro-usos de CPU del cgroup (kernel, page faults), granularidad del período (50/100 ms), ruido de otros procesos del host y jitter del cronometrado desplazan la razón (aquí, frecuencia de CPU turbo y carga del host la elevaron a ≈ 0.64). 0.5 es la fracción <strong>máxima</strong> asignable, no una equivalencia directa con trabajo completado.</p>

<div class="page-break"></div>
<h2 class="section-title">Investigación 5. Síntesis de mecanismos (10 puntos)</h2>

<p><strong>Tabla de síntesis:</strong></p>
<table>
    <thead><tr><th>Mecanismo</th><th>Qué modifica o controla</th><th>Evidencia principal utilizada</th><th>Conclusión incorrecta a evitar</th></tr></thead>
    <tbody>
        <tr><td><strong>PID namespace</strong></td><td>La <strong>vista</strong>/identificación de los PID (qué procesos ve y cómo los numera); no asigna ni limita recursos</td><td><code>NSpid: 824974 1</code>; PID <code>1</code> dentro vs <code>824974</code> desde el host</td><td>"Dos PIDs ⇒ dos procesos" / "el namespace limita CPU o memoria"</td></tr>
        <tr><td><strong>memory.high</strong></td><td><strong>Control</strong> suave de memoria: presión/reclaim/throttle</td><td><code>high</code> Δ = 125, <code>allocation_complete</code> 256 MiB, <code>oom_kill</code> Δ = 0, <code>exit=0</code></td><td>"Es un límite duro de 128 MiB" / "termina al superarlo"</td></tr>
        <tr><td><strong>memory.max</strong></td><td><strong>Control</strong> duro: con swap 0, alcanzar el tope → OOM killer del cgroup</td><td><code>max</code> Δ = 35, <code>oom</code> Δ = 1, <code>oom_kill</code> Δ = 1, <code>exit=137</code>, último <code>allocated_mib</code>=120</td><td>"El proceso falló por sí solo / reportó un error"</td></tr>
        <tr><td><strong>cpu.max</strong></td><td><strong>Control</strong> de CPU: cuota de tiempo por período (throttling CFS)</td><td><code>nr_throttled</code> Δ = 80, <code>throttled_usec</code> Δ ≈ 3.99 s, razón ≈ 0.638</td><td>"Estaba esperando por I/O" / "tardó por carga normal"</td></tr>
    </tbody>
</table>

<h3 class="question-title">5.1. Diferencia entre aislamiento (namespaces) y control de recursos (cgroups).</h3>
<p>Los <strong>namespaces</strong> dan <em>aislamiento</em>: cambian la <strong>vista</strong> del proceso sobre un recurso (Inv. 1: PID <code>1</code> dentro vs <code>824974</code> desde el host, <code>NSpid: 824974 1</code>), pero no acotan cuánto recurso puede usarse. Los <strong>cgroups</strong> son <em>control de recursos</em>: cuantifican y limitan el uso efectivo (Inv. 2/3: <code>memory.events</code> con <code>high</code> Δ=125 y <code>max</code>/<code>oom</code>/<code>oom_kill</code>; Inv. 4: <code>cpu.stat</code> con <code>nr_throttled</code>/<code>throttled_usec</code>). Inv. 1 aporta evidencia de visibilidad; Inv. 2–4 de uso/consumo limitado.</p>

<h3 class="question-title">5.2. Evidencia para distinguir espera, throttling y presión de memoria.</h3>
<ul>
    <li><strong>(a) Espera/bloqueo (Lab 1):</strong> estado del proceso (S/T/D), <code>wchan</code>, <code>iowait</code>/<code>%wa</code> (<code>iostat</code>/<code>mpstat</code>), <code>time</code> con user+sys ≪ <code>real</code>; sin contadores de cgroup de por medio.</li>
    <li><strong>(b) Throttling de CPU (Lab 2):</strong> <code>cpu.stat</code> del cgroup del proceso con Δ <code>nr_throttled</code> y Δ <code>throttled_usec</code> &gt; 0; <code>time</code> con user+sys alto pero avanzando lento, sin estado de espera.</li>
    <li><strong>(c) Presión/límite de memoria (Lab 2):</strong> <code>memory.events</code> con Δ en <code>high</code>/<code>max</code>/<code>oom</code>/<code>oom_kill</code>, <code>memory.current</code> cerca de <code>memory.max</code>, swap con actividad, procesos terminados con <code>137</code>.</li>
</ul>

<h3 class="question-title">5.3. ¿Por qué CPU baja o "tarda más" no basta para identificar el mecanismo?</h3>
<p>"CPU baja" o "tarda más" son síntomas compartidos: un proceso <strong>throttled</strong> consume poca CPU por segundo y avanza poco (similar a una espera de I/O); uno bajo <strong>presión de memoria</strong> se frena por <em>reclaim</em> continuo (CPU baja o wall time con golpes); uno <strong>bloqueado en I/O</strong> muestra CPU baja por otra razón. Para atribuir el mecanismo se necesita la <strong>fuente específica</strong> (contadores de <code>cpu.stat</code>, <code>memory.events</code>, <code>memory.stat</code> pgscan/pgsteal, estado/syscall del proceso) y el contexto (¿está en un cgroup con cuota? ¿cerca de <code>memory.max</code>? ¿esperando I/O?), como se hizo en 4.3 y 5.2.</p>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

subprocess.run([
    "chromium",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_PATH}",
    HTML_PATH,
], check=True, cwd=LAB_DIR)

print(f"Lab02_Guerra_Solorzano.pdf compiled successfully!")