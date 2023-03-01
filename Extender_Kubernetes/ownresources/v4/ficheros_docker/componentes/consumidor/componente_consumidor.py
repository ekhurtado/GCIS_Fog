from kubernetes import client, config
import kafka
import random
import time
from json import loads

def func_consumidor():
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
    consumidor = kafka.KafkaConsumer('topico-datos-procesados', bootstrap_servers= [IP_server + ':9092'], group_id='mi-grupo-consumidores',  value_deserializer=lambda x: loads(x.decode('utf-8')), client_id='mi-consumidor')
    while True:
        for msg in consumidor:
            print('He recibido algo:')
            print(msg)

if __name__ == '__main__':
    func_consumidor()
