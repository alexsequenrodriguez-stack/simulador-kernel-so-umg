# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
pcb.py
Modulo del Bloque de Control de Procesos (PCB).
Cada proceso del simulador se representa con un objeto PCB,
que funciona como la "ficha" donde el kernel guarda sus datos.
"""

# Estados posibles por los que pasa un proceso
NUEVO = "Nuevo"
LISTO = "Listo"
EJECUTANDO = "Ejecutando"
BLOQUEADO = "Bloqueado"
TERMINADO = "Terminado"


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

    def __str__(self):
        """Define como se ve el proceso cuando lo imprimimos en pantalla."""
        return (f"PID {self.pid:<3} | {self.nombre:<10} | {self.estado:<10} | "
                f"{self.tamano_mb:>3} MB | Rafaga restante {self.rafaga_restante}/{self.rafaga_total}")


# Prueba rapida: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    p1 = PCB("Word", 40, 7)
    p2 = PCB("Chrome", 30, 4)
    print(p1)
    print(p2)