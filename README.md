# Laboratorio 2 - Métricas de Software

Este repositorio contiene los workloads y scripts auxiliares del Laboratorio 2.
La guía oficial, las preguntas y los criterios de evaluación se publican en Moodle.

El escenario debe ejecutarse en la máquina virtual oficial del curso.

## Preparar los cgroups

```bash
./prepare.sh
```

## Ejecutar un workload dentro de un cgroup

```bash
./run-in-cgroup.sh <grupo> <comando> [argumentos]
```

Los grupos preparados son `mem-high`, `mem-max` y `cpu-half`.

## Limpiar

```bash
./reset.sh
```
