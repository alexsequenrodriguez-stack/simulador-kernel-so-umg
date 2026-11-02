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
from planificador import PlanificadorRR, comparar_quantums
from semaforo import demo_sin_semaforo, demo_con_semaforo
from deadlock import GestorRecursos
from colores import color, ROJO, VERDE, AMARILLO, CIAN, NEGRITA
import bitacora

# Componentes del kernel simulado
ram = MemoriaRAM(100)
planificador = PlanificadorRR(ram)
gestor = GestorRecursos()
todos_los_procesos = []   # Historial de todos los procesos creados, para poder listarlos


def mostrar_encabezado():
    """Muestra el nombre del simulador al iniciar."""
    print(color("=" * 52, CIAN))
    print(color("   GS-KERNEL  |  Simulador de Funciones del Kernel", NEGRITA))
    print("   Sistemas Operativos I - UMG")
    print(color("=" * 52, CIAN))


def validar_entero(texto, minimo, maximo):
    """
    Revisa si un texto es un numero entero dentro del rango.
    Devuelve (True, numero) si es valido, o (False, mensaje de error) si no lo es.
    """
    try:
        numero = int(texto)
    except ValueError:
        return False, f"'{texto}' no es un numero entero"
    if numero < minimo or numero > maximo:
        return False, f"{numero} esta fuera del rango permitido ({minimo} a {maximo})"
    return True, numero


def leer_entero(mensaje, minimo, maximo):
    """Pide un numero y no deja avanzar hasta que sea valido."""
    while True:
        texto = input(mensaje).strip()
        valido, resultado = validar_entero(texto, minimo, maximo)
        if valido:
            return resultado
        print(color(f"   ERROR: {resultado}. Intente de nuevo.", ROJO))


def buscar_proceso(pid):
    """Busca un proceso por su PID. Devuelve el proceso o None si no existe."""
    for p in todos_los_procesos:
        if p.pid == pid:
            return p
    return None


def cargar_proceso(nombre, tamano, rafaga, memoria, plan):
    """
    Revisa si el proceso cabe en memoria. Si cabe, crea su PCB y lo pone en la cola de listos.
    Si no cabe, lo rechaza con Out of Memory. Devuelve el proceso o None si fue rechazado.
    """
    if tamano > memoria.memoria_libre():
        print(color(f"   ERROR: Out of Memory. '{nombre}' solicita {tamano} MB "
                    f"y solo hay {memoria.memoria_libre()} MB libres. Proceso RECHAZADO.", ROJO))
        bitacora.registrar(f"RECHAZADO '{nombre}' por Out of Memory "
                           f"(pide {tamano} MB, libres {memoria.memoria_libre()} MB)")
        return None

    proceso = PCB(nombre, tamano, rafaga)
    memoria.asignar(proceso.pid, tamano)
    plan.agregar_proceso(proceso)
    print(color("   Proceso creado y cargado en memoria:", VERDE))
    print(f"   {proceso}")
    bitacora.registrar(f"CREADO P{proceso.pid} '{nombre}' | {tamano} MB | rafaga {rafaga}")
    return proceso


def crear_proceso():
    """Opcion 1: pide los datos del proceso y lo intenta cargar."""
    print(color("\n--- CREAR PROCESO ---", NEGRITA))
    nombre = input("Nombre del proceso: ").strip()
    if nombre == "":
        nombre = "Proceso"
    tamano = leer_entero("Tamano en memoria (1-100 MB): ", 1, 100)
    rafaga = leer_entero("Rafaga de CPU (1-50 unidades): ", 1, 50)
    proceso = cargar_proceso(nombre, tamano, rafaga, ram, planificador)
    if proceso is not None:
        todos_los_procesos.append(proceso)


def ver_estado():
    """Opcion 2: muestra la tabla de procesos (PCB), la cola de listos y la memoria."""
    print(color("\n--- ESTADO DEL SISTEMA ---", NEGRITA))
    if len(todos_los_procesos) == 0:
        print("No se ha creado ningun proceso.")
    else:
        for p in todos_los_procesos:
            print(p)
    print(f"\nCola de listos: {planificador.mostrar_cola()}")
    ram.mostrar_estado()

    # Detalle del PCB y del TCB de un proceso, si el usuario lo pide
    if len(todos_los_procesos) > 0:
        texto = input("\nPID para ver su PCB y TCB (Enter para regresar): ").strip()
        if texto != "":
            valido, pid = validar_entero(texto, 1, 9999)
            proceso = buscar_proceso(pid) if valido else None
            if proceso is None:
                print(color("   ERROR: ese PID no existe.", ROJO))
            else:
                proceso.mostrar_detalle()


def eliminar_proceso():
    """Opcion 3: termina un proceso a mano y devuelve su memoria."""
    print(color("\n--- ELIMINAR PROCESO ---", NEGRITA))
    if len(planificador.cola_listos) == 0:
        print("No hay procesos en la cola de listos.")
        return
    print(f"Cola de listos: {planificador.mostrar_cola()}")
    pid = leer_entero("PID del proceso a eliminar: ", 1, 9999)
    proceso = buscar_proceso(pid)
    if proceso is None or proceso not in planificador.cola_listos:
        print(color(f"   ERROR: el PID {pid} no esta en la cola de listos.", ROJO))
        return
    planificador.quitar_proceso(proceso)
    ram.liberar(proceso.pid)
    proceso.estado = TERMINADO
    print(color(f"   P{pid} eliminado. Se liberaron {proceso.tamano_mb} MB.", VERDE))
    bitacora.registrar(f"ELIMINADO P{pid} por el usuario. Libera {proceso.tamano_mb} MB")


def ejecutar_round_robin():
    """Opcion 4: ejecuta Round Robin (normal o paso a paso) y lo compara con FCFS."""
    if len(planificador.cola_listos) == 0:
        print("No hay procesos en la cola de listos.")
        return
    respuesta = input("Modo paso a paso? (s/n): ").strip().lower()
    paso_a_paso = respuesta == "s"
    resumen = planificador.ejecutar(paso_a_paso)
    if resumen is not None:
        bitacora.registrar(
            f"ROUND ROBIN con {resumen['procesos']} procesos | "
            f"Espera RR {resumen['espera_rr']:.2f} vs FCFS {resumen['espera_fcfs']:.2f} | "
            f"Respuesta RR {resumen['respuesta_rr']:.2f} vs FCFS {resumen['respuesta_fcfs']:.2f} | "
            f"Rendimiento {resumen['rendimiento']:.2f}")


def comparar_quantum():
    """Opcion 5: compara quantum 2, 3 y 5 con los procesos de la cola, sin ejecutarlos."""
    if len(planificador.cola_listos) == 0:
        print("No hay procesos en la cola de listos. Cree procesos primero.")
        return
    comparar_quantums(planificador.cola_listos)
    bitacora.registrar(f"COMPARACION DE QUANTUMS con {len(planificador.cola_listos)} procesos")


def simular_semaforo():
    """Opcion 6: demuestra la condicion de carrera sin semaforo y como el semaforo la corrige."""
    print(color("\n--- SEMAFORO Y CONDICION DE CARRERA ---", NEGRITA))
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
    Opcion 7: provoca un deadlock entre dos procesos, lo detecta y el usuario elige cual abortar.
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


def resultado_prueba(nombre, paso):
    """Muestra si una prueba paso o fallo y lo devuelve como 1 o 0 para contarlas."""
    if paso:
        print(color(f"   [OK]    {nombre}", VERDE))
        return 1
    print(color(f"   [FALLO] {nombre}", ROJO))
    return 0


def prueba_de_estres():
    """
    Opcion 8: ejecuta sola todas las pruebas del simulador con un sistema aparte
    (no afecta los procesos que el usuario ya creo) y guarda el resultado en la bitacora.
    """
    print(color("\n=========== PRUEBA DE ESTRES AUTOMATICA ===========", NEGRITA))
    bitacora.registrar("=== PRUEBA DE ESTRES iniciada ===")
    aprobadas = 0

    # Prueba 1: datos invalidos. Ninguno debe ser aceptado.
    print(color("\n[1] Validacion de datos invalidos", CIAN))
    rechazados = 0
    for dato in ["abc", "-5", "500", "3.5", ""]:
        valido, mensaje = validar_entero(dato, 1, 100)
        if not valido:
            rechazados += 1
            print(f"   Entrada '{dato}' -> rechazada: {mensaje}")
    aprobadas += resultado_prueba("Se rechazaron los 5 datos invalidos", rechazados == 5)

    # Prueba 2: desbordamiento de memoria con un sistema de prueba
    print(color("\n[2] Desbordamiento de memoria (Out of Memory)", CIAN))
    ram_prueba = MemoriaRAM(100)
    plan_prueba = PlanificadorRR(ram_prueba)
    for datos in [("Word", 40, 7), ("Chrome", 30, 4), ("Spotify", 20, 3)]:
        cargar_proceso(datos[0], datos[1], datos[2], ram_prueba, plan_prueba)
    rechazado = cargar_proceso("Photoshop", 35, 5, ram_prueba, plan_prueba)
    ram_prueba.mostrar_estado()
    aprobadas += resultado_prueba("Photoshop (35 MB) rechazado con 10 MB libres", rechazado is None)

    # Prueba 3: Round Robin con los 3 procesos cargados
    print(color("\n[3] Planificacion Round Robin", CIAN))
    resumen = plan_prueba.ejecutar(False)
    aprobadas += resultado_prueba("Todos los procesos terminaron y la memoria quedo libre",
                                  resumen is not None and ram_prueba.memoria_usada() == 0)

    # Prueba 4: semaforo contra condicion de carrera
    print(color("\n[4] Semaforo binario contra condicion de carrera", CIAN))
    sin = demo_sin_semaforo(["P1", "P2", "P3"], 100, 50)
    con = demo_con_semaforo(["P1", "P2", "P3"], 100, 50)
    aprobadas += resultado_prueba(f"Sin semaforo dio {sin} (incorrecto) y con semaforo dio {con} (correcto)",
                                  sin != 250 and con == 250)

    # Prueba 5: deadlock, deteccion y recuperacion
    print(color("\n[5] Deteccion y recuperacion de deadlock", CIAN))
    gestor_prueba = GestorRecursos()
    gestor_prueba.forzar_deadlock("PX", "PY")
    detectado = gestor_prueba.verificar() is not None
    gestor_prueba.abortar("PY")
    resuelto = gestor_prueba.verificar() is None
    aprobadas += resultado_prueba("Deadlock detectado y resuelto al abortar PY", detectado and resuelto)

    print(color(f"\nRESULTADO: {aprobadas} de 5 pruebas aprobadas", NEGRITA))
    bitacora.registrar(f"=== PRUEBA DE ESTRES finalizada: {aprobadas}/5 pruebas aprobadas ===")


def menu():
    """Ciclo principal: muestra el menu y ejecuta la opcion elegida hasta que el usuario sale."""
    mostrar_encabezado()
    bitacora.registrar("=== GS-Kernel iniciado ===")

    while True:
        print(color("\n------------- MENU PRINCIPAL -------------", CIAN))
        print(f"Memoria libre: {ram.memoria_libre()} MB | Cola de listos: {planificador.mostrar_cola()}")
        print("1. Crear proceso")
        print("2. Ver procesos y memoria")
        print("3. Eliminar proceso")
        print("4. Ejecutar Round Robin (normal o paso a paso)")
        print("5. Comparar quantums (2, 3 y 5)")
        print("6. Simular semaforo (condicion de carrera)")
        print("7. Simular deadlock")
        print("8. Prueba de estres automatica")
        print("9. Ver bitacora")
        print("0. Salir")
        opcion = leer_entero("Elija una opcion: ", 0, 9)

        if opcion == 1:
            crear_proceso()
        elif opcion == 2:
            ver_estado()
        elif opcion == 3:
            eliminar_proceso()
        elif opcion == 4:
            ejecutar_round_robin()
        elif opcion == 5:
            comparar_quantum()
        elif opcion == 6:
            simular_semaforo()
        elif opcion == 7:
            simular_deadlock()
        elif opcion == 8:
            prueba_de_estres()
        elif opcion == 9:
            bitacora.mostrar()
        else:
            bitacora.registrar("=== GS-Kernel finalizado ===")
            print(color("Saliendo de GS-Kernel...", AMARILLO))
            break


# El programa empieza aqui
if __name__ == "__main__":
    menu()
