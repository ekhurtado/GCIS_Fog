# from kubernetes import client, config
import kafka
from json import dumps, loads
from threading import Thread


def thread_consumidor1(consumidor):
    print("Thread para consumidor 1")

    for msg in consumidor:
        print('He recibido algo del consumidor1.')
        print(msg)

        f = open("transf.txt", "a")
        f.write("CONSUMIDOR1:" + str(msg) + "\n")
        f.close()

        # valor = msg.value * 2
        # productor.send('topico-datos-procesados', value=valor, key=msg.key)   # TODO Descomentarlo: es para pruebas con dos consumers

def thread_consumidor2(consumidor):
    print("Thread para consumidor 2")

    for msg in consumidor:
        print('He recibido algo del consumidor2.')
        print(msg)

        f = open("transf.txt", "a")
        f.write("CONSUMIDOR2:" + str(msg) + "\n")
        f.close()

def func_transformador():
    print("Started")



    print("Configured")

    f = open("transf.txt", "a")
    f.write("Started\n")
    f.close()

    IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"
    print(IP_server)
    consumidor = kafka.KafkaConsumer('topico-datos-crudos', bootstrap_servers= [IP_server + ':9092'], group_id='mi-grupo-transformadores', value_deserializer=lambda x: loads(x.decode('utf-8')),  client_id='mi-consumidor-transformador')
    consumidor2 = kafka.KafkaConsumer('topico-datos-procesados', bootstrap_servers= [IP_server + ':9092'], group_id='mi-grupo-transformadores', value_deserializer=lambda x: loads(x.decode('utf-8')),  client_id='mi-consumidor-transformador')
    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='mi-productor-tranformador', value_serializer=lambda x: dumps(x).encode('utf-8'))

    print('Creados productor y consumidor.')
    while True:
        print('En el bucle.')
        thread1 = Thread(target=thread_consumidor1, args=(consumidor, ))
        thread2 = Thread(target=thread_consumidor2, args=(consumidor2, ))

        thread1.start()
        thread2.start()



if __name__ == '__main__':

    func_transformador()
