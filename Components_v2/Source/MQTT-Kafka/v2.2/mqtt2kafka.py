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

    # En aplicaciones complejas existirá mas de un componente siguiente. Se enviarán los datos a todos los outputs
    moreOutputs = True
    i = 1
    while moreOutputs:
        outputInfo = os.environ.get("OUTPUT_IFMH_TOPIC_" + str(i))
        if outputInfo is not None:
            topic = outputInfo.split(";")[1]
            productor.send(topic, value=topicData, key=os.environ.get('KAFKA_KEY')) # La key es el ID de la
            # aplicacion siempre
            i += 1
        else:
            moreOutputs = False

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
