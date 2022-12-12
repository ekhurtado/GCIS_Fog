import json
from threading import Thread
import kafka
import influx_API

IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"

def printFile(message):
    f = open("sink_influx.txt", "a")
    f.write(str(message) + "\n")
    f.close()

def assembly_station_oee_function_thread():
    printFile("Metodo para guardar datos del OEE de assembly station")
    printFile("Primero, recibiremos los datos por Kafka")

    # Configuracion Kafka Consumer
    consumidor = kafka.KafkaConsumer('topico-datos-oee-influx', bootstrap_servers=[IP_server + ':9092'],
                                     group_id='mi-grupo-transformadores',
                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                     client_id='mi-consumidor-processing')

    # Se detectará cuando alguien publique un mensaje en el tópico
    for msg in consumidor:
        print('He recibido algo del consumidor.')
        print(msg)

        msgJSONValue = msg.value

        machineID = msgJSONValue['machineID']
        data = msgJSONValue['data']

        influx_API.storeData(machineID, data)

def transport_robot_oee_function_thread():
    printFile("Metodo para guardar datos del OEE de transport robot")

def monitor_function_oee_thread():
    printFile("Metodo para guardar datos del OEE del monitor")

def main_sink_influx():
    printFile("Comienzo de ejecución del componente Processing Assembly Station")
    printFile("Started\n")

    # Cada funcion tendrá su hilo de ejecución propio
    while True:
        printFile('En el bucle.')
        thread_func1 = Thread(target=assembly_station_oee_function_thread(), args=())
        thread_func2 = Thread(target=transport_robot_oee_function_thread(), args=())
        thread_func3 = Thread(target=monitor_function_oee_thread(), args=())

        thread_func1.start()
        thread_func2.start()
        thread_func3.start()

if __name__ == '__main__':
    main_sink_influx()