
class Proceso:
    def __init__(self, pid, burst_time, arrival_time, queue, priority):
        self.pid = pid #Etiqueta del proceso
        self.burst_time = burst_time #Burst Time del proceso
        self.remaining_time = burst_time #Remaining Time o tiempo de respuesta
        self.arrival_time = arrival_time #Arrival time o tiempo de llegada
        self.queue = queue #cola a la que pertenece el proceso
        self.priority = priority #prioridad
        self.completion_time = 0 #Completion Time o tiempo de completado
        self.waiting_time = 0 #Waiting Time o tiempo de espera
        self.turnaround_time = 0 #Turnaround Time o tiempo de procesamiento total
        self.response_time = -1  # Para manejar el tiempo de respuesta

    def __repr__(self):
        return f"{self.pid}(BT={self.burst_time}, AT={self.arrival_time}, Q={self.queue}, P={self.priority})"


# Algoritmos de planificación
class FCFS: # First-come, First-served
    def planificar(self, procesos, tiempo_actual):
        procesos.sort(key=lambda p: (p.arrival_time, p.pid)) # Ordenar los procesos por tiempo de llegada y por PID
        for proceso in procesos: # Iterar sobre cada proceso en la lista
            if tiempo_actual < proceso.arrival_time: # Si el tiempo actual es menor que el tiempo de llegada del proceso
                tiempo_actual = proceso.arrival_time # Esperar hasta que el proceso llegue
            proceso.response_time = tiempo_actual - proceso.arrival_time  # Calcular el tiempo de respuesta
            proceso.completion_time = tiempo_actual + proceso.burst_time # Calcular el tiempo de finalización
            proceso.turnaround_time = proceso.completion_time - proceso.arrival_time  # Calcular el turnaround time
            proceso.waiting_time = proceso.turnaround_time - proceso.burst_time # Calcular el tiempo de espera
            tiempo_actual = proceso.completion_time # Actualizar el tiempo actual para el siguiente proceso
        return procesos, tiempo_actual # Se devuelve la lista de procesos con los tiempos calculados y el tiempo actual


class SJF: # Shorted Job First (SJF)
    def planificar(self, procesos, tiempo_actual): 
        procesos_ordenados = [] # Lista para almacenar los procesos en el orden en que se completan
        while procesos: # Mientras haya procesos pendientes se filtran procesos que han llegado hasta el tiempo actual
            disponibles = [p for p in procesos if p.arrival_time <= tiempo_actual]
            if disponibles: # Si hay procesos disponibles para ejecutar se selecciona el proceso con el menor tiempo de ejecución (burst time)
                proceso = min(disponibles, key=lambda p: (p.burst_time, p.pid))
                procesos.remove(proceso) # Se elimina el proceso de la lista original

                if proceso.response_time == -1: # Si se ejecuta un proceso por primera vez
                    proceso.response_time = tiempo_actual # Se registra el tiempo de respuesta

                proceso.completion_time = tiempo_actual + proceso.burst_time # Calcular el tiempo de finalización
                proceso.turnaround_time = proceso.completion_time - proceso.arrival_time # Calcular turnaround time
                proceso.waiting_time = proceso.turnaround_time - proceso.burst_time  # Calcular el tiempo de espera

                tiempo_actual = proceso.completion_time # Actualizar el tiempo actual para el siguiente proceso
                procesos_ordenados.append(proceso) # Añadir el proceso completado a la lista de procesos ordenados
            else:
                tiempo_actual += 1  # Si no hay procesos disponibles se incrementa el tiempo actual
        return procesos_ordenados, tiempo_actual # Se devuelve la lista de procesos con los tiempos calculados y el tiempo actual


class PSJF:
    def planificar(self, procesos, tiempo_actual):
        procesos.sort(key=lambda p: (p.arrival_time, p.pid)) # Ordenar los procesos por tiempo de llegada y por etiqueta
        procesos_ordenados = [] # Lista para almacenar los procesos en el orden en que se completan
        while procesos: # Mientras haya procesos pendientes se filtran procesos que han llegado hasta el tiempo actual
            disponibles = [p for p in procesos if p.arrival_time <= tiempo_actual]
            if disponibles: #Si hay procesos disponibles para ejecutar
                proceso = min(disponibles, key=lambda p: (p.remaining_time, p.pid)) # Seleccionar el proceso con el menor tiempo restante (remaining time)
                ejecucion = 1  # Ejecutar solo por una unidad de tiempo
                proceso.remaining_time -= ejecucion # Reducir el tiempo restante
                tiempo_actual += ejecucion # Incrementar el tiempo actual
                if proceso.response_time == -1: # Si es la primera vez que se está ejecutando el proceso
                    proceso.response_time = tiempo_actual - 1  # Se registra el tiempo de respuesta
                if proceso.remaining_time == 0: # Si el proceso terminó
                    proceso.completion_time = tiempo_actual # Se calcula el tiempo de finalización,
                    proceso.turnaround_time = proceso.completion_time - proceso.arrival_time # el turnaround time,
                    proceso.waiting_time = proceso.turnaround_time - proceso.burst_time # y el tiempo de espera
                    procesos.remove(proceso)  # Se elimina el proceso de la lista original
                    procesos_ordenados.append(proceso) # Añadir el proceso completado a la lista ordenada
            else:
                tiempo_actual += 1 # Si no hay procesos disponibles, incrementar el tiempo actual
        return procesos_ordenados, tiempo_actual # Devolver la lista de procesos ordenados y el tiempo actual


class RoundRobin:
    def __init__(self, quantum):
        self.quantum = quantum

    def planificar(self, procesos, tiempo_actual):
        # Ordenar los procesos por tiempo de llegada
        procesos.sort(key=lambda p: p.arrival_time)
        cant_procesos = len(procesos)
        cola = procesos[:]  # Crear una copia de la lista de procesos
        completados = []  # Lista para almacenar procesos completados
        while len(completados) != cant_procesos:  # Ejecutar hasta que todos los procesos estén completados
            disponibles = [p for p in cola if p.arrival_time <= tiempo_actual]  # Procesos disponibles para ejecutar
            if disponibles:
                proceso = disponibles.pop(0)  # Extraer el primer proceso disponible
                cola.remove(proceso)  # Remover de la cola

                if proceso.response_time == -1:  # Primera vez que se ejecuta
                    proceso.response_time = tiempo_actual - proceso.arrival_time

                # Ejecutar por un tiempo igual al quantum, o hasta que el proceso termine
                if proceso.remaining_time > self.quantum:
                    tiempo_actual += self.quantum
                    proceso.remaining_time -= self.quantum
                    cola.append(proceso)  # Volver a añadir el proceso a la cola si aún no ha terminado
                else:
                    # Si el proceso va a terminar en esta ejecución
                    tiempo_actual += proceso.remaining_time
                    proceso.completion_time = tiempo_actual
                    proceso.turnaround_time = proceso.completion_time - proceso.arrival_time
                    proceso.waiting_time = proceso.turnaround_time - proceso.burst_time
                    completados.append(proceso)  # Añadir proceso completado a la lista de completados
            else:
                tiempo_actual += 1  # No hay procesos disponibles, avanzar el tiempo

        return completados, tiempo_actual 


class MultilevelQueue:
    def __init__(self, alg_colas): # Inicializa con un diccionario de algoritmos para cada cola
        self.alg_colas = alg_colas  # Almacena los algoritmos asignados a cada cola

    def ejecutar(self, procesos): # Método para ejecutar la planificación de procesos
        # Dividir los procesos por colas
        colas = {i: [] for i in self.alg_colas.keys()}  # Se crea un diccionario con claves (colas) y listas vacías
        for proceso in procesos:
            colas[proceso.queue].append(proceso) # Agrupar procesos en la cola correspondiente

        # Inicializar tiempo actual
        tiempo_actual = 0
        ejecutados = [] # Lista para almacenar los procesos ejecutados

        # Ejecutar las colas en orden de prioridad
        for i in colas.keys(): # Ciclo for para iterar sobre las colas
            alg = self.alg_colas[i] # Obtener el algoritmo de planificación para la cola
            procesos_ejecutados, tiempo_actual = alg.planificar(colas[i], tiempo_actual) # Planificar procesos en la cola
            ejecutados.extend(procesos_ejecutados) # Añadir los procesos ejecutados a la lista

        return ejecutados # Devolver la lista de procesos ejecutados


# Leer y escribir archivos
def leer_procesos(archivo):
    procesos = []
    with open(archivo, 'r') as f:
        lines = f.readlines()[2:]  # Saltar las dos primeras líneas
        for line in lines:
            datos = line.strip().split('; ')
            pid = datos[0]
            burst_time = int(datos[1])
            arrival_time = int(datos[2])
            queue = int(datos[3])
            priority = int(datos[4])
            procesos.append(Proceso(pid, burst_time, arrival_time, queue, priority))
    return procesos


def calcular_promedios(procesos_ejecutados): # Se calculan los promedios totales de cada métrica
    wating_time_prom = sum([proceso.waiting_time for proceso in procesos_ejecutados]) / len(procesos_ejecutados)
    completion_time_prom = sum([proceso.completion_time for proceso in procesos_ejecutados]) / len(procesos_ejecutados)
    response_time_prom = sum([proceso.response_time for proceso in procesos_ejecutados]) / len(procesos_ejecutados)
    turnaround_time_prom = sum([proceso.turnaround_time for proceso in procesos_ejecutados]) / len(procesos_ejecutados)
    promedios = f"\nWT={wating_time_prom}; CT={completion_time_prom}; RT={response_time_prom}; TAT={turnaround_time_prom}"
    return promedios


def generar_salida(procesos, promedios, archivo_salida): # Función para generar el archivo de salida requerido
    with open(archivo_salida, 'w') as f:
        f.write("# archivo de salida\n")
        f.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
        for proceso in procesos:
            f.write(f"{proceso.pid};{proceso.burst_time};{proceso.arrival_time};"
                     f"{proceso.queue};{proceso.priority};{proceso.waiting_time};"
                     f"{proceso.completion_time};{proceso.response_time};"
                     f"{proceso.turnaround_time}\n")
        f.write(promedios)

# Solicitar al usuario el nombre del archivo de entrada
archivo_entrada = input('Escriba el archivo de entrada: mlq0')
archivo_salida = 'mlq0' + archivo_entrada + '_salida.txt'
archivo_entrada = 'mlq0' + archivo_entrada + '.txt'

# Definir algoritmos para cada cola
print("Menú de esquemas:")
print('''1. RR(1), RR(3), SJF.
2. RR(3), RR(5), FCFS.
3. RR(2), RR(3), STCF.''')
opcion = 0 # Inicializar opción
# Validar la entrada del usuario para asegurarse de que el número está entre 1 y 3
while opcion < 1 or opcion > 3:
    try:
        opcion = int(input("Escoja el esquema que desea implementar: "))
    except ValueError:
        print("Por favor, introduzca un número válido.") # Manejo de errores

if opcion == 1:
    alg_colas = {
        1: RoundRobin(quantum=1), # Cola 1: Round Robin con quantum = 1
        2: RoundRobin(quantum=3), # Cola 2: Round Robin con quantum de 3
        3: SJF() # Cola 3: Shortest Job First
    }
elif opcion == 2:
    alg_colas = {
        1: RoundRobin(quantum=3), # Cola 1: Round Robin con quantum = 3
        2: RoundRobin(quantum=5), # Cola 2: Round Robin con quantum = 3
        3: FCFS() # Cola 3: Preemptive Shortest Job First
    }
elif opcion == 3:
    alg_colas = {
        1: RoundRobin(quantum=2),
        2: RoundRobin(quantum=3),
        3: PSJF()
    }
# Leer los procesos desde el archivo de entrada
procesos = leer_procesos(archivo_entrada) 
mlq = MultilevelQueue(alg_colas) # Crear una instancia de MultilevelQueue
procesos_ejecutados = mlq.ejecutar(procesos) # Ejecutar los procesos utilizando el algoritmo de colas múltiples
promedios = calcular_promedios(procesos_ejecutados) # Calcular los tiempos promedios de los procesos ejecutados
generar_salida(procesos_ejecutados, promedios, archivo_salida)