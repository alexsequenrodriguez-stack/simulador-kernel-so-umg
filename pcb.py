# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
pcb.py
Modulo del Bloque de Control de Procesos (PCB).
Cada proceso del simulador se representa con un objeto PCB,
que funciona como la "ficha" donde el kernel guarda sus datos.
"""

from colores import color, color_estado

# Estados posibles por los que pasa un proceso
NUEVO = "Nuevo"
LISTO = "Listo"
EJECUTANDO = "Ejecutando"
BLOQUEADO = "Bloqueado"
TERMINADO = "Terminado"

class TCB:
    """
    Bloque de Control de Hilo (TCB): la "ficha" de un hilo dentro de un proceso.
    El PCB describe al proceso completo (su memoria, su rafaga); el TCB describe
    al hilo que realmente usa el CPU. En este simulador cada proceso tiene un solo hilo.
    """

    siguiente_tid = 1   # Contador para asignar TIDs unicos (1, 2, 3...)

    def __init__(self, pid):
        self.tid = TCB.siguiente_tid
        TCB.siguiente_tid += 1
        self.pid = pid      # Proceso al que pertenece este hilo


class PCB:
    """Bloque de Control de Procesos: guarda la informacion de un proceso."""

    # Contador compartido por todos los procesos para asignar PIDs unicos (1, 2, 3...)
    siguiente_pid = 1

    def __init__(self, nombre, tamano_mb, rafaga_total):
        # PID: identificador unico, como el numero de ticket en el banco
        self.pid = PCB.siguiente_pid
        PCB.siguiente_pid += 1

        self.nombre = nombre                  # Nombre para reconocerlo facil (ej. "Chrome")
        self.estado = NUEVO                   # Estado actual del proceso
        self.tamano_mb = tamano_mb            # Cuanta memoria RAM ocupa
        self.rafaga_total = rafaga_total      # Tiempo total de CPU que necesita
        self.rafaga_restante = rafaga_total   # Tiempo de CPU que le falta (baja en cada turno)

        # Datos que sirven al final para calcular tiempos de retorno, espera y respuesta
        self.tiempo_llegada = 0
        self.tiempo_primera_ejecucion = None
        self.tiempo_finalizacion = None
        
        # Cada proceso se crea con su hilo principal (TCB)
        self.tcb = TCB(self.pid)

    def __str__(self):
        """Define como se ve el proceso al imprimirlo. El estado sale con su color."""
        estado = color(f"{self.estado:<10}", color_estado(self.estado))
        return (f"PID {self.pid:<3} | {self.nombre:<10} | {estado} | "
                f"{self.tamano_mb:>3} MB | Rafaga restante {self.rafaga_restante}/{self.rafaga_total}")

    def mostrar_detalle(self):
        """Muestra toda la ficha del proceso (PCB) y la de su hilo (TCB)."""
        estado = color(self.estado, color_estado(self.estado))
        print("   --- PCB (Bloque de Control de Proceso) ---")
        print(f"   PID: {self.pid}  |  Nombre: {self.nombre}  |  Estado: {estado}")
        print(f"   Memoria asignada: {self.tamano_mb} MB")
        print(f"   Rafaga total: {self.rafaga_total}  |  Rafaga restante: {self.rafaga_restante}")
        print("   --- TCB (Bloque de Control de Hilo) ---")
        print(f"   TID: {self.tcb.tid}  |  Pertenece al proceso PID {self.pid}")
        print(f"   Estado del hilo: {estado}")
        # El contador de programa indica cuanto trabajo del hilo ya se ejecuto
        print(f"   Contador de programa: {self.rafaga_total - self.rafaga_restante} de {self.rafaga_total} unidades")


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    p1 = PCB("Word", 40, 7)
    p2 = PCB("Chrome", 30, 4)
    print(p1)
    print(p2)
