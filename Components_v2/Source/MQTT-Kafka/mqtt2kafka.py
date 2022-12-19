import os
import kafka

IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"


def assembly_station_function(message):
    print("Hilo de ejecución para la función 'get Assembly Station Data'")
    print("Vamos a enviar los datos recogidos de la estacion de montaje al elemento Sink mediante Kafka")
    topicData = str(message).split("'")[1]

    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='source-mqtt-kafka',
                                    value_serializer=str.encode,
                                    key_serializer=str.encode)
    productor.send('topico-datos-assembly-mqtt', value=topicData, key=os.environ.get('KAFKA_KEY'))

    # subscriber.subscribe(client=client, clientName=clientName, topic="#", on_message_method=process_assembly_message)


def transport_robot_function():
    print("Hilo de ejecución para la función 'get Transport Robot Data'")


def monitor_function():
    print("Hilo de ejecución para la función 'get Monitor Data'")


# def main_mqtt2kafka():
#     print("Comienzo de ejecución del componente Source MQTT-Kafka")
#     print("Started\n")
#
#     # Cada funcion tendrá su hilo de ejecución propio
#     while True:
#         print('En el bucle.')
#         thread_func1 = Thread(target=assembly_station_function_thread(), args=())
#         thread_func2 = Thread(target=transport_robot_function_thread(), args=())
#         thread_func3 = Thread(target=monitor_function_thread(), args=())
#
#         thread_func1.start()
#         thread_func2.start()
#         thread_func3.start()
#
#
# if __name__ == '__main__':
#     main_mqtt2kafka()
