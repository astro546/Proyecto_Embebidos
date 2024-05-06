import threading
from threading import Semaphore
import time

NTHREADS = 20
WIDTH = 1

shared_variable = 0  # Variable compartida entre hilos
shared_time = 0  # Variable compartida para el tiempo actual
numero_hilos = NTHREADS  # Número de hilos a crear
hilos = []  # Lista para almacenar los objetos hilo

def funcion_hilo(id_hilo):
  global shared_variable, shared_time  # Declarar variables globales

  while True:
    # Modificar la variable compartida
    shared_variable += 1
    print(f"Hilo {id_hilo}: valor compartido = {shared_variable}")

    # Simular trabajo del hilo (retardo basado en ID)
    time.sleep(id_hilo+1)

if __name__ == "__main__":
  for i in range(numero_hilos):
    # Crear un nuevo hilo y pasarlo a la función
    hilo = threading.Thread(target=funcion_hilo, args=(i,))
    hilos.append(hilo)  # Agregar el hilo a la lista

  # Iniciar todos los hilos
  for hilo in hilos:
    hilo.start()

  # Esperar a que todos los hilos terminen (opcional)
"""   for hilo in hilos:
    hilo.join() """