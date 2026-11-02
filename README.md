# GS-Kernel - Simulador de funciones del Kernel

Proyecto final del curso Sistemas Operativos I
Universidad Mariano Galvez de Guatemala - Centro Universitario Boca del Monte

Autor: Gerardo Sequen
Carne: 7690-24-16803

## Descripcion

GS-Kernel es un simulador por consola que imita algunas de las tareas que realiza el
kernel de un sistema operativo: crear y administrar procesos, asignar memoria, repartir
el CPU entre procesos y controlar el acceso a recursos compartidos.

No controla procesos reales de la computadora; todo se simula con estructuras de datos
en Python para poder observar paso a paso lo que haria el sistema operativo.

## Que incluye

- Procesos: cada proceso tiene su PCB (PID, estado, memoria, rafaga) y su TCB (hilo).
- Memoria: RAM de 100 MB con asignacion continua dinamica. Si un proceso no cabe,
  se rechaza con error Out of Memory.
- Planificacion: algoritmo Round Robin con quantum = 3. Muestra los cambios de contexto,
  el diagrama de Gantt, los tiempos de retorno, espera y respuesta, y lo compara con FCFS.
  Tambien permite comparar el resultado con quantum 2, 3 y 5.
- Concurrencia: semaforo binario (wait / signal) protegiendo una variable compartida.
  Se muestra el mismo caso sin semaforo (condicion de carrera) y con semaforo.
- Deadlock: se fuerza una espera circular entre dos procesos, el sistema detecta el
  ciclo en el grafo de asignacion de recursos y se resuelve abortando uno de ellos.
- Prueba de estres automatica y bitacora de eventos (bitacora.txt).

## Requisitos

- Python 3.10 o superior (se probo con Python 3.14)
- No necesita instalar librerias externas

## Como ejecutarlo

Desde la carpeta del proyecto:

    python main.py

Se recomienda usar la terminal de VS Code o la terminal de Windows para que se vean
los colores.

## Archivos

| Archivo | Contenido |
|---|---|
| main.py | Menu principal y validacion de datos |
| pcb.py | Estructura del proceso (PCB) y del hilo (TCB) |
| memoria.py | Gestion de la memoria RAM |
| planificador.py | Round Robin, comparacion con FCFS y entre quantums |
| semaforo.py | Semaforo binario y demostracion de condicion de carrera |
| deadlock.py | Simulacion, deteccion y recuperacion del interbloqueo |
| bitacora.py | Registro de eventos en bitacora.txt |
| colores.py | Colores para la consola |

## Decisiones tomadas

- Quantum de 3: al comparar con 2 y 5, el quantum 3 mantiene una buena respuesta
  sin hacer tantos cambios de contexto.
- Semaforo binario: solo se necesita que un proceso a la vez modifique la variable
  compartida, por lo que un semaforo de 0 y 1 es suficiente.
- Deadlock por deteccion y recuperacion: no requiere conocer de antemano cuantos
  recursos pedira cada proceso; cuando se detecta el ciclo se termina un proceso
  para liberar sus recursos.
