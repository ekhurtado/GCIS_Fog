from threading import Thread
import kafka

import subscriber

IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"


def process_assembly_message(client, userdata, message):
    print("Datos del topico: " + str(message.topic))
    topicData = str(message.payload).split("'")[1]
    print("Vamos a enviar los datos recogidos a Kafka")

    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='source-mqtt-kafka',
                                    value_serializer=str.encode,
                                    key_serializer=str.encode)
    productor.send('topico-datos-assembly-mqtt', value=topicData, key='App-1')


def assembly_station_function_thread():
    print("Hilo de ejecución para la función 'get Assembly Station Data'")
    print("Vamos a enviar los datos recogidos de la estacion de montaje al elemento Sink")

    subscriber.subscribe(clientName="source-assembly-station", topic="#", on_message_method=process_assembly_message)


def transport_robot_function_thread():
    print("Hilo de ejecución para la función 'get Transport Robot Data'")


def monitor_function_thread():
    print("Hilo de ejecución para la función 'get Monitor Data'")


def main_mqtt2kafka():
    print("Comienzo de ejecución del componente Source MQTT-Kafka")
    print("Started\n")

    # Cada funcion tendrá su hilo de ejecución propio
    while True:
        print('En el bucle.')
        thread_func1 = Thread(target=assembly_station_function_thread(), args=())
        thread_func2 = Thread(target=transport_robot_function_thread(), args=())
        thread_func3 = Thread(target=monitor_function_thread(), args=())

        thread_func1.start()
        thread_func2.start()
        thread_func3.start()


if __name__ == '__main__':
    main_mqtt2kafka()
