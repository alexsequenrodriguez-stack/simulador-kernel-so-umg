# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
deadlock.py
Modulo de Interbloqueo (Deadlock).
Hay dos recursos exclusivos (R1 y R2). Se fuerza una espera circular entre dos procesos,
el sistema la detecta con el grafo de asignacion de recursos (RAG) y la resuelve
abortando uno de los procesos.
Notacion del grafo:  R -> P = el recurso esta ASIGNADO al proceso
                     P -> R = el proceso SOLICITA el recurso
Estrategia: Deteccion del ciclo y Recuperacion por terminacion de procesos.
"""

from colores import color, ROJO, VERDE, AMARILLO, NEGRITA


class GestorRecursos:
    """Lleva el control de quien tiene cada recurso y quien esta esperando uno."""

    def __init__(self):
        self.dueno = {"R1": None, "R2": None}   # Recurso -> proceso que lo tiene (None = libre)
        self.espera = {}                        # Proceso -> recurso que esta pidiendo

    def solicitar(self, proceso, recurso):
        """Un proceso pide un recurso. Si esta libre se lo dan, si lo tiene otro, se queda esperando."""
        if self.dueno[recurso] is None:
            self.dueno[recurso] = proceso
            print(f"   {proceso} pide {recurso} -> ASIGNADO")
        elif self.dueno[recurso] == proceso:
            print(f"   {proceso} ya tiene {recurso}")
        else:
            self.espera[proceso] = recurso
            print(color(f"   {proceso} pide {recurso} -> lo tiene {self.dueno[recurso]}. "
                        f"{proceso} queda ESPERANDO", AMARILLO))

    def forzar_deadlock(self, proceso_a, proceso_b):
        self.dueno = {"R1": None, "R2": None}
        self.espera = {}
        print(color(f"\n--- SIMULACION DE INTERBLOQUEO entre {proceso_a} y {proceso_b} ---", NEGRITA))
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
        """Corre la deteccion y muestra el ciclo del grafo con las 4 condiciones de Coffman."""
        atrapados = self.detectar()
        if atrapados is None:
            print(color("\n   Sin deadlock: no existe ciclo de espera en el grafo.", VERDE))
            return None

        a = atrapados[0]
        b = atrapados[1]
        # Ciclo con la notacion de clase: P -> R (solicita) -> P (asignado) -> ...
        ciclo = f"{a} -> {self.espera[a]} -> {b} -> {self.espera[b]} -> {a}"
        print(color(f"\n   !!! DEADLOCK DETECTADO. Ciclo de espera: {ciclo}", ROJO))
        print("   Se cumplen las 4 condiciones de Coffman:")
        print("     1. Exclusion mutua: cada recurso solo lo usa un proceso a la vez")
        print("     2. Retencion (contencion) y espera: cada proceso tiene un recurso y pide otro")
        print("     3. No apropiacion: nadie le puede quitar el recurso a otro")
        print("     4. Espera circular: cada uno espera al otro")
        return atrapados

    def abortar(self, proceso):
        """Termina a la fuerza un proceso, suelta sus recursos y se los da a quien los esperaba."""
        print(color(f"\n   ABORTANDO {proceso}...", ROJO))
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
                        print(color(f"   {recurso} se asigna a {otro}, que deja de esperar", VERDE))
                        break

    def mostrar_estado(self):
        """Muestra el grafo de asignacion de recursos (RAG) con flechas."""
        print("   Grafo de asignacion de recursos:")
        for recurso in self.dueno:
            if self.dueno[recurso] is None:
                print(f"     {recurso}: libre")
            else:
                print(f"     {recurso} -> {self.dueno[recurso]}   (asignado)")
        for proceso in self.espera:
            print(f"     {proceso} -> {self.espera[proceso]}   (solicita)")


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    gestor = GestorRecursos()
    gestor.forzar_deadlock("P1", "P2")
    gestor.mostrar_estado()
    gestor.verificar()
    gestor.abortar("P2")
    gestor.mostrar_estado()
    gestor.verificar()
