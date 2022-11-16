from kubernetes import client, config
import kafka
from json import dumps, loads


def func_transformador():
    print("Started")

    config.load_incluster_config()

    print("Configured")

    cliente = client.CoreV1Api()
    servicios =cliente.list_namespaced_service("kafka-ns")
    j = 0
    for i in servicios.items:
        print(i.metadata.name)
        if 'bootstrap' in i.metadata.name:
            break
        j = j + 1
    IP_server = servicios.items[j].spec.cluster_ip
    # IP_server = "mi-cluster-kafka-bootstrap"
    print(IP_server)
    consumidor = kafka.KafkaConsumer('topico-datos-crudos', bootstrap_servers= [IP_server + ':9092'], group_id='mi-grupo-transformadores', value_deserializer=lambda x: loads(x.decode('utf-8')),  client_id='mi-consumidor-transformador')
    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='mi-productor-tranformador', value_serializer=lambda x: dumps(x).encode('utf-8'))
    print('Creados productor y consumidor.')
    while True:
        print('En el bucle.')
        for msg in consumidor:
            print('He recibido algo.')
            print(msg)
            valor = msg.value * 2
            productor.send('topico-datos-procesados', value=valor, key=msg.key)

if __name__ == '__main__':
    func_transformador()
