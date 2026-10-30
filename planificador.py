"""
planificador.py
Modulo de Planificacion de Procesos con el algoritmo Round Robin (RR).
Cada proceso de la cola de listos recibe turnos de CPU de maximo q = 3 unidades (quantum).
Si al agotar el quantum el proceso no ha terminado, se realiza un cambio de contexto
y el proceso regresa al final de la cola de listos.
"""

from collections import deque
from pcb import LISTO, EJECUTANDO, TERMINADO

QUANTUM = 3  # Tiempo maximo de CPU que recibe un proceso en cada turno


class PlanificadorRR:
    """Planificador de corto plazo que reparte el CPU por turnos (Round Robin)."""

    def __init__(self, memoria, quantum=QUANTUM):
        self.memoria = memoria          # Referencia a la RAM para liberar espacio cuando un proceso termina
        self.quantum = quantum          # Tamano del turno de CPU
        self.cola_listos = deque()      # Fila de procesos que esperan el CPU (el primero es el siguiente en ejecutar)
        self.reloj = 0                  # Reloj del sistema en unidades de tiempo simuladas
        self.terminados = []            # Historial de procesos que ya finalizaron

    def agregar_proceso(self, proceso):
        """Coloca un proceso al final de la cola de listos y registra su tiempo de llegada."""
        proceso.estado = LISTO
        proceso.tiempo_llegada = self.reloj
        self.cola_listos.append(proceso)

    def mostrar_cola(self):
        """Devuelve el contenido de la cola de listos en formato de texto, del primero al ultimo."""
        if not self.cola_listos:
            return "[] (vacia)"
        return "[" + ", ".join(f"P{p.pid}" for p in self.cola_listos) + "]"

    def ejecutar(self):
        """Ejecuta todos los procesos de la cola de listos usando Round Robin hasta que terminen."""
        if not self.cola_listos:
            print("No hay procesos en la cola de listos.")
            return

        print(f"\n=== PLANIFICACION ROUND ROBIN (quantum = {self.quantum}) ===")
        print(f"Cola inicial: {self.mostrar_cola()}\n")

        linea_gantt = []        # Guarda cada turno (pid, inicio, fin) para dibujar el diagrama de Gantt
        terminados_ahora = []   # Procesos que terminan en esta ejecucion

        while self.cola_listos:
            # 1. El despachador toma el primer proceso de la cola y le asigna el CPU
            proceso = self.cola_listos.popleft()
            proceso.estado = EJECUTANDO

            # Se registra la primera vez que el proceso usa el CPU (para el tiempo de respuesta)
            if proceso.tiempo_primera_ejecucion is None:
                proceso.tiempo_primera_ejecucion = self.reloj

            # 2. El proceso ejecuta el quantum completo o lo que le falte, lo que sea menor
            tiempo_turno = min(self.quantum, proceso.rafaga_restante)
            inicio = self.reloj
            self.reloj += tiempo_turno
            proceso.rafaga_restante -= tiempo_turno
            linea_gantt.append((proceso.pid, inicio, self.reloj))

            print(f"[t={inicio:>3} -> {self.reloj:>3}] P{proceso.pid} ({proceso.nombre}) ejecuta "
                  f"{tiempo_turno} u. | Restante: {proceso.rafaga_restante}")

            # 3. Se decide que pasa con el proceso al terminar su turno
            if proceso.rafaga_restante == 0:
                proceso.estado = TERMINADO
                proceso.tiempo_finalizacion = self.reloj
                self.memoria.liberar(proceso.pid)
                terminados_ahora.append(proceso)
                print(f"   -> P{proceso.pid} TERMINO. Libera {proceso.tamano_mb} MB de memoria.")
            else:
                proceso.estado = LISTO
                self.cola_listos.append(proceso)
                print(f"   -> Quantum agotado. Cambio de contexto: P{proceso.pid} regresa al final de la cola.")

            print(f"   Cola de listos: {self.mostrar_cola()}")

        self.terminados.extend(terminados_ahora)
        self.mostrar_gantt(linea_gantt)
        self.mostrar_metricas(terminados_ahora)

    def mostrar_gantt(self, linea):
        """Dibuja el diagrama de Gantt con el orden en que los procesos usaron el CPU."""
        print("\nDiagrama de Gantt:")
        barras = "|"
        tiempos = str(linea[0][1])
        for pid, inicio, fin in linea:
            barras += f"{'P' + str(pid):^6}|"
            tiempos = tiempos.ljust(len(barras) - 1) + str(fin)
        print(barras)
        print(tiempos)

    def mostrar_metricas(self, procesos):
        """Calcula y muestra los tiempos de retorno, espera y respuesta de cada proceso y sus promedios."""
        print("\nFormulas: Retorno = Fin - Llegada | Espera = Retorno - Rafaga | Respuesta = Primera CPU - Llegada")
        print(f"{'PID':<6}{'Llegada':>8}{'Rafaga':>8}{'Fin':>6}{'Retorno':>9}{'Espera':>8}{'Respuesta':>11}")

        total_retorno = total_espera = total_respuesta = 0
        for p in sorted(procesos, key=lambda x: x.pid):
            retorno = p.tiempo_finalizacion - p.tiempo_llegada
            espera = retorno - p.rafaga_total
            respuesta = p.tiempo_primera_ejecucion - p.tiempo_llegada
            total_retorno += retorno
            total_espera += espera
            total_respuesta += respuesta
            print(f"{'P' + str(p.pid):<6}{p.tiempo_llegada:>8}{p.rafaga_total:>8}"
                  f"{p.tiempo_finalizacion:>6}{retorno:>9}{espera:>8}{respuesta:>11}")

        n = len(procesos)
        print(f"\nPromedio de retorno:   {total_retorno / n:.2f}")
        print(f"Promedio de espera:    {total_espera / n:.2f}")
        print(f"Promedio de respuesta: {total_respuesta / n:.2f}")


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    from pcb import PCB
    from memoria import MemoriaRAM

    ram = MemoriaRAM()
    planificador = PlanificadorRR(ram)

    for nombre, tamano, rafaga in [("Word", 40, 7), ("Chrome", 30, 4), ("Spotify", 20, 3)]:
        proceso = PCB(nombre, tamano, rafaga)
        ram.asignar(proceso.pid, tamano)
        planificador.agregar_proceso(proceso)

    planificador.ejecutar()