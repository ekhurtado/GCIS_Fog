import json
import os
from threading import Thread
import kafka
import influx_API

IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"
Kafka_key = os.environ.get('KAFKA_KEY')

def printFile(message):
    f = open("sink_influx.txt", "a")
    f.write(str(message) + "\n")
    f.close()

def assembly_station_oee_function_thread():
    printFile("Metodo para guardar datos del OEE de assembly station")
    printFile("Primero, recibiremos los datos por Kafka")

    # Configuracion Kafka Consumer
    consumidor = kafka.KafkaConsumer(os.environ.get('KAFKA_TOPIC'), bootstrap_servers=[IP_server + ':9092'],
                                     group_id='mi-grupo-transformadores',
                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                     key_deserializer=lambda x: x.decode('utf-8'),
                                     client_id='mi-consumidor-processing')

    # Se detectará cuando alguien publique un mensaje en el tópico
    for msg in consumidor:
        print('He recibido algo del consumidor.')
        print(msg)

        msgJSONValue = msg.value

        machineID = msgJSONValue['machineID']
        data = msgJSONValue['data']

        msg_key = msg.key.split("'")[1] # tenemos que hacer esto ya que no se deserializa bien, viene en forma: b'<key>'

        if Kafka_key == msg_key:

            influx_API.storeData(machineID, data)

        else:
            printFile("This message is not for this component (key does not match)")

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