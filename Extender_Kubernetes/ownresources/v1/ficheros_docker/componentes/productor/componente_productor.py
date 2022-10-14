from kubernetes import client, config
import kafka
import random
import time
from json import dumps

def func_productor():
    #config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    config.load_incluster_config()
    cliente = client.CoreV1Api()
    servicios=cliente.list_namespaced_service("default")
    j = 0
    for i in servicios.items:
        if 'bootstrap' in i.metadata.name:
            break
        j = j + 1
    IP_server = servicios.items[j].spec.cluster_ip
    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='mi-productor', value_serializer=lambda x: dumps(x).encode('utf-8'))
    #test=productor.bootstrap_connected()
    while True:
        numero = random.randrange(0,10,1)        
        print(numero)
        productor.send('topico-datos-crudos', value=numero) # b'Hola'
        # productor.flush()
        time.sleep(2)

if __name__ == '__main__':
    func_productor()
