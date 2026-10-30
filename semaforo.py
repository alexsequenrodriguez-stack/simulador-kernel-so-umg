# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
semaforo.py
Modulo de Concurrencia y Sincronizacion.
Implementa un Semaforo Binario con las operaciones wait() y signal() para proteger
una Variable Global Compartida (seccion critica).
Incluye una demostracion de condicion de carrera: primero sin semaforo (resultado incorrecto)
y despues con semaforo (resultado correcto).
"""


class SemaforoBinario:
    """Semaforo binario: solo deja que un proceso a la vez este en la seccion critica."""

    def __init__(self):
        self.valor = 1           # 1 = seccion critica libre, 0 = ocupada
        self.cola_espera = []    # Procesos bloqueados esperando su turno para entrar
        self.dueno = None        # Proceso que esta dentro de la seccion critica

    def wait(self, proceso):
        """
        Pedir la llave. Si la seccion critica esta libre, el proceso entra;
        si esta ocupada, se va a la cola de espera (queda bloqueado).
        """
        if self.valor == 1:
            self.valor = 0
            self.dueno = proceso
            print(f"   wait({proceso}): seccion critica libre -> {proceso} ENTRA (semaforo = 0)")
            return True
        self.cola_espera.append(proceso)
        print(f"   wait({proceso}): ocupada por {self.dueno} -> {proceso} BLOQUEADO. "
              f"Cola de espera: [{', '.join(self.cola_espera)}]")
        return False

    def signal(self, proceso):
        """
        Devolver la llave. Si hay alguien en la cola de espera, el primero entra directo;
        si no hay nadie, la seccion critica queda libre.
        Devuelve el proceso que entra, o None si queda libre.
        """
        if len(self.cola_espera) > 0:
            siguiente = self.cola_espera.pop(0)
            self.dueno = siguiente
            print(f"   signal({proceso}): {proceso} SALE y despierta a {siguiente}, que ENTRA")
            return siguiente
        self.valor = 1
        self.dueno = None
        print(f"   signal({proceso}): {proceso} SALE. Seccion critica libre (semaforo = 1)")
        return None


def demo_sin_semaforo(procesos, saldo_inicial, deposito):
    """
    Condicion de carrera: todos los procesos leen la variable global antes de que
    alguno guarde su resultado, por eso se pierden depositos.
    """
    print(f"\n--- SIN SEMAFORO: {len(procesos)} procesos depositan {deposito} al mismo tiempo ---")
    variable_global = saldo_inicial
    lecturas = {}

    # Todos leen el mismo valor porque nadie controla el acceso
    for p in procesos:
        lecturas[p] = variable_global
        print(f"   {p} lee la variable global = {variable_global}")

    # Cada uno guarda su calculo encima del anterior
    for p in procesos:
        variable_global = lecturas[p] + deposito
        print(f"   {p} guarda {lecturas[p]} + {deposito} = {variable_global}")

    esperado = saldo_inicial + deposito * len(procesos)
    print(f"   Resultado final: {variable_global} | Esperado: {esperado}")
    print("   -> CONDICION DE CARRERA: se perdieron depositos porque nadie controlo el acceso.")
    return variable_global


def demo_con_semaforo(procesos, saldo_inicial, deposito):
    """Mismo escenario, pero la variable global se protege con el semaforo binario."""
    print(f"\n--- CON SEMAFORO BINARIO: {len(procesos)} procesos depositan {deposito} ---")
    semaforo = SemaforoBinario()
    variable_global = saldo_inicial

    # Todos intentan entrar al mismo tiempo: solo uno lo logra y el resto espera
    for p in procesos:
        semaforo.wait(p)

    # Uno por uno usa la seccion critica y al salir le pasa el turno al siguiente
    actual = semaforo.dueno
    while actual is not None:
        lectura = variable_global
        variable_global = lectura + deposito
        print(f"   [{actual} en seccion critica] lee {lectura} y guarda {lectura} + {deposito} = {variable_global}")
        actual = semaforo.signal(actual)

    esperado = saldo_inicial + deposito * len(procesos)
    print(f"   Resultado final: {variable_global} | Esperado: {esperado}")
    print("   -> CORRECTO: el semaforo garantizo la exclusion mutua.")
    return variable_global


# Prueba rapida del modulo: solo se ejecuta cuando este archivo se corre directamente
if __name__ == "__main__":
    demo_sin_semaforo(["P1", "P2"], 100, 50)
    demo_con_semaforo(["P1", "P2"], 100, 50)
