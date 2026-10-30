# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
deadlock.py
Modulo de Interbloqueo (Deadlock).
Hay dos recursos exclusivos (R1 y R2). Se fuerza una espera circular entre dos procesos,
el sistema la detecta y la resuelve abortando uno de los procesos.
Estrategia: Deteccion y Recuperacion por terminacion de procesos.
"""


class GestorRecursos:
    """Lleva el control de quien tiene cada recurso y quien esta esperando uno."""

    def __init__(self):
        self.dueno = {"R1": None, "R2": None}   # Recurso -> proceso que lo tiene (None = libre)
        self.espera = {}                        # Proceso -> recurso que esta pidiendo

    def solicitar(self, proceso, recurso):
        """Un proceso pide un recurso. Si esta libre se lo dan; si lo tiene otro, se queda esperando."""
        if self.dueno[recurso] is None:
            self.dueno[recurso] = proceso
            print(f"   {proceso} pide {recurso} -> ASIGNADO")
        elif self.dueno[recurso] == proceso:
            print(f"   {proceso} ya tiene {recurso}")
        else:
            self.espera[proceso] = recurso
            print(f"   {proceso} pide {recurso} -> lo tiene {self.dueno[recurso]}. {proceso} queda ESPERANDO")

    def forzar_deadlock(self, proceso_a, proceso_b):
        """Arma la trampa: A toma R1 y pide R2; B toma R2 y pide R1. Ninguno puede seguir."""
        self.dueno = {"R1": None, "R2": None}
        self.espera = {}
        print(f"\n--- SIMULACION DE INTERBLOQUEO entre {proceso_a} y {proceso_b} ---")
        self.solicitar(proceso_a, "R1")
        self.solicitar(proceso_b, "R2")
        self.solicitar(proceso_a, "R2")
        self.solicitar(proceso_b, "R1")

    def detectar(self):
        """
        Busca una espera circular: el proceso A espera un recurso que tiene B,
        y B espera un recurso que tiene A. Si pasa eso, hay deadlock.
        Devuelve los dos procesos atrapados, o None si no hay deadlock.
        """
        for proceso in self.espera:
            recurso_pedido = self.espera[proceso]
            otro = self.dueno[recurso_pedido]            # Quien tiene lo que este proceso pide
            if otro in self.espera:                      # Ese otro tambien esta esperando algo?
                recurso_del_otro = self.espera[otro]
                if self.dueno[recurso_del_otro] == proceso:   # Y lo que espera lo tiene el primero?
                    return [proceso, otro]
        return None

    def verificar(self):
        """Corre la deteccion y muestra el resultado con las 4 condiciones de Coffman."""
        atrapados = self.detectar()
        if atrapados is None:
            print("\n   Sin deadlock: no existe espera circular.")
            return None

        a = atrapados[0]
        b = atrapados[1]
        print(f"\n   !!! DEADLOCK DETECTADO: {a} -> {b} -> {a}")
        print("   Condiciones de Coffman presentes:")
        print("     1. Exclusion mutua: cada recurso solo lo usa un proceso a la vez")
        print("     2. Retencion y espera: cada proceso tiene un recurso y pide otro")
        print("     3. No apropiacion: nadie le puede quitar el recurso a otro")
        print("     4. Espera circular: cada uno espera al otro")
        return atrapados

    def abortar(self, proceso):
        """Termina a la fuerza un proceso, suelta sus recursos y se los da a quien los esperaba."""
        print(f"\n   ABORTANDO {proceso}...")
        if proceso in self.espera:
            del self.espera[proceso]

        for recurso in self.dueno:
            if self.dueno[recurso] == proceso:
                self.dueno[recurso] = None
                print(f"   {proceso} libera {recurso}")
                # Si alguien esperaba este recurso, ahora se le asigna
                for otro in self.espera:
                    if self.espera[otro] == recurso:
                        self.dueno[recurso] = otro
                        del self.espera[otro]
                        print(f"   {recurso} se asigna a {otro}, que deja de esperar")
                        break

    def mostrar_estado(self):
        """Muestra quien tiene cada recurso y quien esta esperando."""
        print("   Estado de recursos:")
        for recurso in self.dueno:
            if self.dueno[recurso] is None:
                print(f"     {recurso}: libre")
            else:
                print(f"     {recurso}: lo tiene {self.dueno[recurso]}")
        for proceso in self.espera:
            print(f"     {proceso} espera {self.espera[proceso]}")


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    gestor = GestorRecursos()
    gestor.forzar_deadlock("P1", "P2")
    gestor.mostrar_estado()
    gestor.verificar()
    gestor.abortar("P2")
    gestor.mostrar_estado()
    gestor.verificar()