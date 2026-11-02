# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
colores.py
Colores para la consola. No necesita instalar nada: usa los codigos de color ANSI
que ya entienden la terminal de VS Code y la consola de Windows.
Cada color es un texto especial que se pone antes del mensaje, y FIN regresa al color normal.
"""

import os

# En Windows esta linea activa los colores en la consola (en VS Code ya vienen activos)
os.system("")

ROJO = "\033[91m"
VERDE = "\033[92m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
MAGENTA = "\033[95m"
CIAN = "\033[96m"
GRIS = "\033[90m"
NEGRITA = "\033[1m"
FIN = "\033[0m"

# Colores para distinguir a cada proceso en el diagrama de Gantt
COLORES_PROCESOS = [CIAN, MAGENTA, AMARILLO, AZUL, VERDE]


def color(texto, codigo):
    """Pinta un texto con el color indicado y despues regresa al color normal."""
    return codigo + str(texto) + FIN


def color_proceso(pid):
    """Devuelve el color de un proceso segun su PID (el P1 siempre tiene el mismo color)."""
    return COLORES_PROCESOS[(pid - 1) % len(COLORES_PROCESOS)]


def color_estado(estado):
    """Color de cada estado del proceso."""
    if estado == "Listo":
        return AMARILLO
    if estado == "Ejecutando":
        return VERDE
    if estado == "Bloqueado":
        return ROJO
    if estado == "Terminado":
        return GRIS
    return AZUL   
