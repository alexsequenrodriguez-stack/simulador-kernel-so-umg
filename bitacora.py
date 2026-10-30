# Proyecto Final - Sistemas Operativos I
# Universidad Mariano Galvez de Guatemala
# Autor: Gerardo Sequen
"""
bitacora.py
Modulo de Bitacora del sistema.
Cada evento importante del simulador (proceso creado, rechazado, terminado, deadlock, etc.)
se guarda con fecha y hora en el archivo bitacora.txt, como lo haria el registro (log) de un kernel.
Este archivo sirve como evidencia de las pruebas realizadas.
"""

import os
from datetime import datetime

# El archivo se guarda en la misma carpeta donde estan los archivos del programa
CARPETA = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(CARPETA, "bitacora.txt")


def registrar(evento):
    """Agrega una linea a la bitacora con la fecha y hora del evento."""
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARCHIVO, "a", encoding="utf-8") as archivo:
        archivo.write(f"[{hora}] {evento}\n")


def mostrar():
    """Muestra en pantalla todo lo que se ha guardado en la bitacora."""
    if not os.path.exists(ARCHIVO):
        print("La bitacora esta vacia.")
        return
    print("\n=== BITACORA DEL SISTEMA (bitacora.txt) ===")
    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        print(archivo.read())
