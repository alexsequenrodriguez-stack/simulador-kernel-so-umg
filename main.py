# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
main.py
GS-Kernel: Simulador de Funciones del Kernel.
Es el menu principal desde donde se usan todos los modulos:
PCB, gestion de memoria, Round Robin, semaforo y deadlock.
Todas las entradas del usuario se validan para que el programa no se caiga
con datos incorrectos (letras, negativos, valores fuera de rango).
"""

from pcb import PCB, TERMINADO
from memoria import MemoriaRAM
from planificador import PlanificadorRR
from semaforo import demo_sin_semaforo, demo_con_semaforo
from deadlock import GestorRecursos
import bitacora

# Componentes del kernel simulado
ram = MemoriaRAM(100)
planificador = PlanificadorRR(ram)
gestor = GestorRecursos()
todos_los_procesos = []   # Historial de todos los procesos creados, para poder listarlos


def mostrar_encabezado():
    """Muestra el nombre del simulador al iniciar."""
    print("=" * 50)
    print("   GS-KERNEL  |  Simulador de Funciones del Kernel")
    print("   Sistemas Operativos I - UMG")
    print("=" * 50)


def leer_entero(mensaje, minimo, maximo):
    """
    Pide un numero entero y no deja avanzar hasta que sea valido.
    Rechaza letras, decimales, negativos y valores fuera del rango permitido.
    """
    while True:
        texto = input(mensaje).strip()
        try:
            numero = int(texto)
        except ValueError:
            print(f"   ERROR: '{texto}' no es un numero entero. Intente de nuevo.")
            continue
        if numero < minimo or numero > maximo:
            print(f"   ERROR: el valor debe estar entre {minimo} y {maximo}. Intente de nuevo.")
            continue
        return numero


def buscar_proceso(pid):
    """Busca un proceso por su PID. Devuelve el proceso o None si no existe."""
    for p in todos_los_procesos:
        if p.pid == pid:
            return p
    return None


def crear_proceso():
    """Opcion 1: pide los datos del proceso, revisa si cabe en memoria y lo pone en la cola."""
    print("\n--- CREAR PROCESO ---")
    nombre = input("Nombre del proceso: ").strip()
    if nombre == "":
        nombre = "Proceso"
    tamano = leer_entero("Tamano en memoria (1-100 MB): ", 1, 100)
    rafaga = leer_entero("Rafaga de CPU (1-50 unidades): ", 1, 50)

    # Antes de crear el proceso se revisa si hay memoria suficiente
    if tamano > ram.memoria_libre():
        print(f"   ERROR: Out of Memory. '{nombre}' solicita {tamano} MB "
              f"y solo hay {ram.memoria_libre()} MB libres. Proceso RECHAZADO.")
        bitacora.registrar(f"RECHAZADO '{nombre}' por Out of Memory "
                           f"(pide {tamano} MB, libres {ram.memoria_libre()} MB)")
        return

    proceso = PCB(nombre, tamano, rafaga)
    ram.asignar(proceso.pid, tamano)
    planificador.agregar_proceso(proceso)
    todos_los_procesos.append(proceso)
    print(f"   Proceso creado y cargado en memoria:\n   {proceso}")
    bitacora.registrar(f"CREADO P{proceso.pid} '{nombre}' | {tamano} MB | rafaga {rafaga}")


def ver_estado():
    """Opcion 2: muestra la tabla de procesos (PCB), la cola de listos y la memoria."""
    print("\n--- ESTADO DEL SISTEMA ---")
    if len(todos_los_procesos) == 0:
        print("No se ha creado ningun proceso.")
    else:
        for p in todos_los_procesos:
            print(p)
    print(f"\nCola de listos: {planificador.mostrar_cola()}")
    ram.mostrar_estado()


def eliminar_proceso():
    """Opcion 3: termina un proceso a mano y devuelve su memoria."""
    print("\n--- ELIMINAR PROCESO ---")
    if len(planificador.cola_listos) == 0:
        print("No hay procesos en la cola de listos.")
        return
    print(f"Cola de listos: {planificador.mostrar_cola()}")
    pid = leer_entero("PID del proceso a eliminar: ", 1, 9999)
    proceso = buscar_proceso(pid)
    if proceso is None or proceso not in planificador.cola_listos:
        print(f"   ERROR: el PID {pid} no esta en la cola de listos.")
        return
    planificador.quitar_proceso(proceso)
    ram.liberar(proceso.pid)
    proceso.estado = TERMINADO
    print(f"   P{pid} eliminado. Se liberaron {proceso.tamano_mb} MB.")
    bitacora.registrar(f"ELIMINADO P{pid} por el usuario. Libera {proceso.tamano_mb} MB")


def ejecutar_round_robin():
    """Opcion 4: ejecuta Round Robin con los procesos de la cola y lo compara con FCFS."""
    resumen = planificador.ejecutar()
    if resumen is not None:
        bitacora.registrar(
            f"ROUND ROBIN ejecutado con {resumen['procesos']} procesos | "
            f"Espera RR {resumen['espera_rr']:.2f} vs FCFS {resumen['espera_fcfs']:.2f} | "
            f"Respuesta RR {resumen['respuesta_rr']:.2f} vs FCFS {resumen['respuesta_fcfs']:.2f}")


def simular_semaforo():
    """Opcion 5: demuestra la condicion de carrera sin semaforo y como el semaforo la corrige."""
    print("\n--- SEMAFORO Y CONDICION DE CARRERA ---")
    cantidad = leer_entero("Cuantos procesos depositan a la vez (2-5): ", 2, 5)
    saldo = leer_entero("Saldo inicial de la variable global (0-10000): ", 0, 10000)
    deposito = leer_entero("Monto que deposita cada proceso (1-1000): ", 1, 1000)

    procesos = []
    for i in range(1, cantidad + 1):
        procesos.append("P" + str(i))

    resultado_sin = demo_sin_semaforo(procesos, saldo, deposito)
    resultado_con = demo_con_semaforo(procesos, saldo, deposito)
    bitacora.registrar(f"SEMAFORO: {cantidad} procesos, saldo {saldo}, deposito {deposito} | "
                       f"sin semaforo = {resultado_sin}, con semaforo = {resultado_con}")


def simular_deadlock():
    """
    Opcion 6: provoca un deadlock entre dos procesos, lo detecta y el usuario elige cual abortar.
    Si hay al menos 2 procesos en la cola se usan esos; si no, se usan dos procesos de prueba.
    """
    if len(planificador.cola_listos) >= 2:
        proceso_a = planificador.cola_listos[0]
        proceso_b = planificador.cola_listos[1]
        nombre_a = "P" + str(proceso_a.pid)
        nombre_b = "P" + str(proceso_b.pid)
    else:
        proceso_a = None
        proceso_b = None
        nombre_a = "PA"
        nombre_b = "PB"
        print("\n(Hay menos de 2 procesos en la cola: se usan dos procesos de prueba, PA y PB)")

    gestor.forzar_deadlock(nombre_a, nombre_b)
    gestor.mostrar_estado()
    if gestor.verificar() is None:
        return
    bitacora.registrar(f"DEADLOCK detectado entre {nombre_a} y {nombre_b}")

    print("\nPara romper el interbloqueo hay que abortar uno de los dos procesos.")
    opcion = leer_entero(f"Abortar 1) {nombre_a}  o  2) {nombre_b}: ", 1, 2)
    if opcion == 1:
        victima = nombre_a
        proceso_victima = proceso_a
    else:
        victima = nombre_b
        proceso_victima = proceso_b

    gestor.abortar(victima)

    # Si la victima es un proceso real, tambien sale de la cola y libera su memoria
    if proceso_victima is not None:
        planificador.quitar_proceso(proceso_victima)
        ram.liberar(proceso_victima.pid)
        proceso_victima.estado = TERMINADO
        print(f"   {victima} sale del sistema y libera {proceso_victima.tamano_mb} MB de memoria.")

    gestor.mostrar_estado()
    gestor.verificar()
    bitacora.registrar(f"RECUPERACION: se aborto {victima}, deadlock resuelto")


def menu():
    """Ciclo principal: muestra el menu y ejecuta la opcion elegida hasta que el usuario sale."""
    mostrar_encabezado()
    bitacora.registrar("=== GS-Kernel iniciado ===")

    while True:
        print("\n----------- MENU PRINCIPAL -----------")
        print(f"Memoria libre: {ram.memoria_libre()} MB | Cola de listos: {planificador.mostrar_cola()}")
        print("1. Crear proceso")
        print("2. Ver procesos y memoria")
        print("3. Eliminar proceso")
        print("4. Ejecutar Round Robin (y comparar con FCFS)")
        print("5. Simular semaforo (condicion de carrera)")
        print("6. Simular deadlock")
        print("7. Ver bitacora")
        print("0. Salir")
        opcion = leer_entero("Elija una opcion: ", 0, 7)

        if opcion == 1:
            crear_proceso()
        elif opcion == 2:
            ver_estado()
        elif opcion == 3:
            eliminar_proceso()
        elif opcion == 4:
            ejecutar_round_robin()
        elif opcion == 5:
            simular_semaforo()
        elif opcion == 6:
            simular_deadlock()
        elif opcion == 7:
            bitacora.mostrar()
        else:
            bitacora.registrar("=== GS-Kernel finalizado ===")
            print("Saliendo de GS-Kernel...")
            break


# El programa empieza aqui
if __name__ == "__main__":
    menu()
