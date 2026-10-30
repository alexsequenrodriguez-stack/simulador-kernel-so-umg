# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
memoria.py
Modulo de Gestion de Memoria.
Simula una memoria RAM fisica de 100 MB usando Asignacion Continua Dinamica:
cada proceso recibe exactamente el espacio que solicita, siempre que haya suficiente libre.
Si no hay espacio, el proceso se rechaza con un error de desbordamiento (Out of Memory).
"""


class MemoriaRAM:
    """Administrador de memoria: controla cuanto espacio esta ocupado y por cual proceso."""

    def __init__(self, capacidad_mb=100):
        self.capacidad_mb = capacidad_mb      # Tamano total de la RAM simulada
        self.asignaciones = {}                # Registro del espacio de cada proceso: {pid: tamano_mb}

    def memoria_usada(self):
        """Suma el espacio de todos los procesos cargados en memoria."""
        return sum(self.asignaciones.values())

    def memoria_libre(self):
        """Espacio disponible = capacidad total - espacio usado."""
        return self.capacidad_mb - self.memoria_usada()

    def asignar(self, pid, tamano_mb):
        """
        Intenta reservar memoria para un proceso.
        Devuelve True si se asigno el espacio, o False si no alcanza (Out of Memory).
        """
        if tamano_mb > self.memoria_libre():
            return False
        self.asignaciones[pid] = tamano_mb
        return True

    def liberar(self, pid):
        """Devuelve a la RAM el espacio de un proceso que termino o fue eliminado."""
        if pid in self.asignaciones:
            del self.asignaciones[pid]

    def mostrar_estado(self):
        """Muestra una barra visual del uso de memoria (cada simbolo representa 5 MB)."""
        usada = self.memoria_usada()
        bloques_usados = usada // 5
        bloques_libres = (self.capacidad_mb // 5) - bloques_usados
        barra = "#" * bloques_usados + "-" * bloques_libres
        print(f"RAM [{barra}] {usada}/{self.capacidad_mb} MB usados | {self.memoria_libre()} MB libres")
        for pid, tamano in self.asignaciones.items():
            print(f"   PID {pid}: {tamano} MB")


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    ram = MemoriaRAM()
    pruebas = [(1, 40), (2, 30), (3, 35)]

    for pid, tamano in pruebas:
        if ram.asignar(pid, tamano):
            print(f"PID {pid}: se asignaron {tamano} MB")
        else:
            print(f"PID {pid}: ERROR Out of Memory - solicita {tamano} MB "
                  f"y solo hay {ram.memoria_libre()} MB libres")

    ram.mostrar_estado()
    print("Se libera el PID 1...")
    ram.liberar(1)
    ram.mostrar_estado()