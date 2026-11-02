# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
planificador.py
Modulo de Planificacion de Procesos con el algoritmo Round Robin (RR).
Cada proceso de la cola de listos recibe turnos de CPU de maximo q = 3 unidades (quantum).
Si al agotar el quantum el proceso no ha terminado, se hace un cambio de contexto
y el proceso regresa al final de la cola de listos.
Incluye:
 - Modo paso a paso (cada turno avanza con Enter)
 - Rendimiento: procesos terminados por unidad de tiempo
 - Comparacion con FCFS y comparacion de distintos quantums
"""

from pcb import LISTO, EJECUTANDO, TERMINADO
from colores import color, color_proceso, VERDE, AMARILLO, CIAN, NEGRITA, GRIS

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
            pid = self.cola_listos[i].pid
            texto += color("P" + str(pid), color_proceso(pid))
            if i < len(self.cola_listos) - 1:
                texto += ", "
        return texto + "]"

    def ejecutar(self, paso_a_paso=False):
        """
        Ejecuta todos los procesos de la cola con Round Robin hasta que terminen.
        Si paso_a_paso es True, el programa se detiene despues de cada turno hasta presionar Enter.
        Devuelve un resumen con los promedios para guardarlo en la bitacora.
        """
        if len(self.cola_listos) == 0:
            print("No hay procesos en la cola de listos.")
            return None

        # Copia de los procesos en el orden en que llegaron (para la tabla y para FCFS)
        procesos = list(self.cola_listos)
        reloj_inicial = self.reloj
        turnos = []              # Cada turno se guarda como (pid, inicio, fin) para el diagrama de Gantt
        cambios_contexto = 0

        print(color(f"\n=== PLANIFICACION ROUND ROBIN (quantum = {self.quantum}) ===", NEGRITA))
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

            nombre = color(f"P{proceso.pid} ({proceso.nombre})", color_proceso(proceso.pid))
            print(f"[t={inicio:>3} -> {self.reloj:>3}] CPU: {nombre} ejecuta "
                  f"{tiempo_turno} u. | Restante: {proceso.rafaga_restante}")

            # 3. Si ya no le falta nada, termina; si le falta, regresa al final de la fila
            if proceso.rafaga_restante == 0:
                proceso.estado = TERMINADO
                proceso.tiempo_finalizacion = self.reloj
                self.memoria.liberar(proceso.pid)
                print(color(f"   -> P{proceso.pid} TERMINO. Libera {proceso.tamano_mb} MB de memoria.", VERDE))
            else:
                proceso.estado = LISTO
                self.cola_listos.append(proceso)
                cambios_contexto = cambios_contexto + 1
                print(color(f"   -> Quantum agotado. Cambio de contexto: P{proceso.pid} "
                            f"regresa al final de la cola.", AMARILLO))

            print(f"   Cola de listos: {self.mostrar_cola()}")

            # Modo paso a paso: se espera a que el usuario presione Enter para el siguiente turno
            if paso_a_paso and len(self.cola_listos) > 0:
                input(color("   [Enter] siguiente turno...", GRIS))

        self.mostrar_gantt(turnos)
        espera_rr, respuesta_rr = self.mostrar_metricas(procesos)

        # Rendimiento = procesos terminados / tiempo total que tardaron
        tiempo_total = self.reloj - reloj_inicial
        rendimiento = len(procesos) / tiempo_total
        print(f"Cambios de contexto realizados: {cambios_contexto}")
        print(f"Rendimiento: {len(procesos)} procesos / {tiempo_total} u. de tiempo = "
              f"{rendimiento:.2f} procesos por unidad de tiempo")

        espera_fcfs, respuesta_fcfs = comparar_con_fcfs(procesos, reloj_inicial)

        return {
            "procesos": len(procesos),
            "espera_rr": espera_rr,
            "respuesta_rr": respuesta_rr,
            "espera_fcfs": espera_fcfs,
            "respuesta_fcfs": respuesta_fcfs,
            "rendimiento": rendimiento,
        }

    def mostrar_gantt(self, turnos):
        """Dibuja el diagrama de Gantt: en que orden usaron el CPU los procesos (cada uno con su color)."""
        print(color("\nDiagrama de Gantt:", NEGRITA))
        barras = "|"
        tiempos = ""
        for turno in turnos:
            pid = turno[0]
            inicio = turno[1]
            etiqueta = "P" + str(pid)
            # Cada casilla mide 7 caracteres: "|" + 6 de contenido
            casilla = "  " + etiqueta + " " * (4 - len(etiqueta))
            barras += color(casilla, color_proceso(pid)) + "|"
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

    print(color("\n=== COMPARACION: ROUND ROBIN vs FCFS (mismos procesos) ===", NEGRITA))
    print(f"{'':<22}{'Round Robin':>12}{'FCFS':>8}")
    print(f"{'Espera promedio':<22}{espera_rr:>12.2f}{espera_fcfs:>8.2f}")
    print(f"{'Respuesta promedio':<22}{respuesta_rr:>12.2f}{respuesta_fcfs:>8.2f}")

    if respuesta_rr < respuesta_fcfs:
        print(color("-> Round Robin atiende a todos mas rapido la primera vez (mejor respuesta).", VERDE))
    elif respuesta_rr == respuesta_fcfs:
        print("-> La respuesta fue igual en los dos algoritmos.")
    else:
        print(color("-> En este caso FCFS respondio mas rapido.", AMARILLO))

    if espera_rr > espera_fcfs:
        print(color("-> A cambio, RR tuvo mas espera total por los cambios de contexto.", AMARILLO))
    return espera_fcfs, respuesta_fcfs


def simular_rr(rafagas, quantum):
    """
    Simula Round Robin solo con numeros, sin tocar los procesos reales.
    rafagas es una lista con la rafaga de cada proceso, en orden de llegada (todos llegan en t=0).
    Devuelve: espera promedio, respuesta promedio, cambios de contexto y rendimiento.
    """
    n = len(rafagas)
    restante = list(rafagas)            # Lo que le falta a cada proceso
    primera_vez = [None] * n            # Cuando uso el CPU por primera vez
    fin = [0] * n                       # Cuando termino
    cola = list(range(n))               # La cola guarda la posicion de cada proceso
    reloj = 0
    cambios = 0

    while len(cola) > 0:
        i = cola.pop(0)
        if primera_vez[i] is None:
            primera_vez[i] = reloj
        turno = min(quantum, restante[i])
        reloj = reloj + turno
        restante[i] = restante[i] - turno
        if restante[i] == 0:
            fin[i] = reloj
        else:
            cola.append(i)
            cambios = cambios + 1

    total_espera = 0
    total_respuesta = 0
    for i in range(n):
        total_espera += fin[i] - rafagas[i]      # Espera = Retorno - Rafaga (llegada = 0)
        total_respuesta += primera_vez[i]
    return total_espera / n, total_respuesta / n, cambios, n / reloj


def comparar_quantums(procesos, quantums=(2, 3, 5)):
    """
    Corre los mismos procesos con distintos quantums para ver cual conviene.
    No ejecuta los procesos reales: solo calcula los resultados.
    """
    rafagas = []
    for p in procesos:
        rafagas.append(p.rafaga_restante)

    print(color("\n=== COMPARACION DE QUANTUMS (mismos procesos) ===", NEGRITA))
    print(f"Rafagas: {rafagas}")
    print(f"{'Quantum':<10}{'Espera prom.':>14}{'Respuesta prom.':>17}{'Cambios ctx':>13}")
    resultados = []
    for q in quantums:
        espera, respuesta, cambios, rendimiento = simular_rr(rafagas, q)
        resultados.append((q, espera, respuesta, cambios))
        fila = f"{'q = ' + str(q):<10}{espera:>14.2f}{respuesta:>17.2f}{cambios:>13}"
        if q == QUANTUM:
            fila = color(fila + "  <- usado", CIAN)
        print(fila)

    print("-> Quantum pequeno: responde mas rapido pero hace mas cambios de contexto.")
    print("-> Quantum grande: menos cambios, pero se parece a FCFS y responde mas lento.")
    print(f"-> El rendimiento es igual en todos ({rendimiento:.2f} procesos por unidad de tiempo) porque")
    print("   el trabajo total es el mismo; el quantum solo cambia el ORDEN en que se atiende.")
    return resultados


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
    comparar_quantums(planificador.cola_listos)
    planificador.ejecutar()
