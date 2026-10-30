# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
planificador.py
Modulo de Planificacion de Procesos con el algoritmo Round Robin (RR).
Cada proceso de la cola de listos recibe turnos de CPU de maximo q = 3 unidades (quantum).
Si al agotar el quantum el proceso no ha terminado, se hace un cambio de contexto
y el proceso regresa al final de la cola de listos.
Al terminar, se comparan los resultados con FCFS usando los mismos procesos.
"""

from pcb import LISTO, EJECUTANDO, TERMINADO

QUANTUM = 3  # Tiempo maximo de CPU que recibe un proceso en cada turno


class PlanificadorRR:
    """Planificador que reparte el CPU por turnos (Round Robin)."""

    def __init__(self, memoria, quantum=QUANTUM):
        self.memoria = memoria       # La RAM, para liberar espacio cuando un proceso termina
        self.quantum = quantum       # Tamano del turno de CPU
        self.cola_listos = []        # Fila de procesos que esperan el CPU (el de la posicion 0 es el siguiente)
        self.reloj = 0               # Reloj del sistema en unidades de tiempo simuladas

    def agregar_proceso(self, proceso):
        """Pone un proceso al final de la cola de listos y anota a que hora llego."""
        proceso.estado = LISTO
        proceso.tiempo_llegada = self.reloj
        self.cola_listos.append(proceso)

    def quitar_proceso(self, proceso):
        """Saca un proceso de la cola de listos (se usa cuando se elimina o se aborta)."""
        if proceso in self.cola_listos:
            self.cola_listos.remove(proceso)

    def mostrar_cola(self):
        """Arma un texto con la cola de listos, del primero al ultimo. Ejemplo: [P1, P2, P3]"""
        if len(self.cola_listos) == 0:
            return "[] (vacia)"
        texto = "["
        for i in range(len(self.cola_listos)):
            texto += "P" + str(self.cola_listos[i].pid)
            if i < len(self.cola_listos) - 1:
                texto += ", "
        return texto + "]"

    def ejecutar(self):
        """
        Ejecuta todos los procesos de la cola con Round Robin hasta que terminen.
        Devuelve un resumen con los promedios para guardarlo en la bitacora.
        """
        if len(self.cola_listos) == 0:
            print("No hay procesos en la cola de listos.")
            return None

        # Se guarda una copia de los procesos en el orden en que llegaron (para la tabla y para FCFS)
        procesos = list(self.cola_listos)
        reloj_inicial = self.reloj
        turnos = []              # Cada turno se guarda como (pid, inicio, fin) para el diagrama de Gantt
        cambios_contexto = 0

        print(f"\n=== PLANIFICACION ROUND ROBIN (quantum = {self.quantum}) ===")
        print(f"Cola inicial: {self.mostrar_cola()}\n")

        while len(self.cola_listos) > 0:
            # 1. Se saca al primero de la fila y se le da el CPU
            proceso = self.cola_listos.pop(0)
            proceso.estado = EJECUTANDO

            # Si es la primera vez que usa el CPU, se anota (sirve para el tiempo de respuesta)
            if proceso.tiempo_primera_ejecucion is None:
                proceso.tiempo_primera_ejecucion = self.reloj

            # 2. Usa el CPU el quantum completo, o menos si le falta menos
            tiempo_turno = min(self.quantum, proceso.rafaga_restante)
            inicio = self.reloj
            self.reloj = self.reloj + tiempo_turno
            proceso.rafaga_restante = proceso.rafaga_restante - tiempo_turno
            turnos.append((proceso.pid, inicio, self.reloj))

            print(f"[t={inicio:>3} -> {self.reloj:>3}] P{proceso.pid} ({proceso.nombre}) ejecuta "
                  f"{tiempo_turno} u. | Restante: {proceso.rafaga_restante}")

            # 3. Si ya no le falta nada, termina; si le falta, regresa al final de la fila
            if proceso.rafaga_restante == 0:
                proceso.estado = TERMINADO
                proceso.tiempo_finalizacion = self.reloj
                self.memoria.liberar(proceso.pid)
                print(f"   -> P{proceso.pid} TERMINO. Libera {proceso.tamano_mb} MB de memoria.")
            else:
                proceso.estado = LISTO
                self.cola_listos.append(proceso)
                cambios_contexto = cambios_contexto + 1
                print(f"   -> Quantum agotado. Cambio de contexto: P{proceso.pid} regresa al final de la cola.")

            print(f"   Cola de listos: {self.mostrar_cola()}")

        self.mostrar_gantt(turnos)
        espera_rr, respuesta_rr = self.mostrar_metricas(procesos)
        print(f"Cambios de contexto realizados: {cambios_contexto}")
        espera_fcfs, respuesta_fcfs = comparar_con_fcfs(procesos, reloj_inicial)

        return {
            "procesos": len(procesos),
            "espera_rr": espera_rr,
            "respuesta_rr": respuesta_rr,
            "espera_fcfs": espera_fcfs,
            "respuesta_fcfs": respuesta_fcfs,
        }

    def mostrar_gantt(self, turnos):
        """Dibuja el diagrama de Gantt: en que orden usaron el CPU los procesos."""
        print("\nDiagrama de Gantt:")
        barras = "|"
        tiempos = ""
        for turno in turnos:
            pid = turno[0]
            inicio = turno[1]
            etiqueta = "P" + str(pid)
            # Cada casilla mide 7 caracteres: "|" + 6 de contenido
            barras += "  " + etiqueta + " " * (4 - len(etiqueta)) + "|"
            tiempos += str(inicio) + " " * (7 - len(str(inicio)))
        tiempos += str(turnos[-1][2])   # El ultimo tiempo es cuando termina todo
        print(barras)
        print(tiempos)

    def mostrar_metricas(self, procesos):
        """Calcula los tiempos de retorno, espera y respuesta de cada proceso y sus promedios."""
        print("\nFormulas: Retorno = Fin - Llegada | Espera = Retorno - Rafaga | Respuesta = Primera CPU - Llegada")
        print(f"{'PID':<6}{'Llegada':>8}{'Rafaga':>8}{'Fin':>6}{'Retorno':>9}{'Espera':>8}{'Respuesta':>11}")

        total_retorno = 0
        total_espera = 0
        total_respuesta = 0
        for p in procesos:
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
        return total_espera / n, total_respuesta / n


def comparar_con_fcfs(procesos, reloj_inicial):
    """
    Calcula como le hubiera ido a los MISMOS procesos con FCFS (el primero que llega
    usa el CPU hasta terminar, sin turnos) y lo compara con Round Robin.
    """
    reloj = reloj_inicial
    total_espera_fcfs = 0
    total_espera_rr = 0
    total_respuesta_rr = 0

    for p in procesos:
        # En FCFS el proceso empieza cuando el anterior termina, y no se interrumpe
        inicio = reloj
        reloj = reloj + p.rafaga_total
        total_espera_fcfs += inicio - p.tiempo_llegada     # En FCFS la espera es igual a la respuesta
        total_espera_rr += (p.tiempo_finalizacion - p.tiempo_llegada) - p.rafaga_total
        total_respuesta_rr += p.tiempo_primera_ejecucion - p.tiempo_llegada

    n = len(procesos)
    espera_fcfs = total_espera_fcfs / n
    respuesta_fcfs = espera_fcfs
    espera_rr = total_espera_rr / n
    respuesta_rr = total_respuesta_rr / n

    print("\n=== COMPARACION: ROUND ROBIN vs FCFS (mismos procesos) ===")
    print(f"{'':<22}{'Round Robin':>12}{'FCFS':>8}")
    print(f"{'Espera promedio':<22}{espera_rr:>12.2f}{espera_fcfs:>8.2f}")
    print(f"{'Respuesta promedio':<22}{respuesta_rr:>12.2f}{respuesta_fcfs:>8.2f}")

    if respuesta_rr < respuesta_fcfs:
        print("-> Round Robin atiende a todos mas rapido la primera vez (mejor respuesta).")
    elif respuesta_rr == respuesta_fcfs:
        print("-> La respuesta fue igual en los dos algoritmos.")
    else:
        print("-> En este caso FCFS respondio mas rapido.")

    if espera_rr > espera_fcfs:
        print("-> A cambio, RR tuvo mas espera total por los cambios de contexto.")
    return espera_fcfs, respuesta_fcfs


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    from pcb import PCB
    from memoria import MemoriaRAM

    ram = MemoriaRAM()
    planificador = PlanificadorRR(ram)
    for datos in [("Word", 40, 7), ("Chrome", 30, 4), ("Spotify", 20, 3)]:
        proceso = PCB(datos[0], datos[1], datos[2])
        ram.asignar(proceso.pid, proceso.tamano_mb)
        planificador.agregar_proceso(proceso)
    planificador.ejecutar()
