import os

from kubernetes import client, config
import kafka
import random
import time
from json import loads

def func_consumidor():
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace("Extender_Kubernetes\pruebasEkaitz\pruebasKafka", "")
    print(os.path.join(os.path.abspath(path), "k3s.yaml"))

    # config.load_kube_config("k3s.yaml")  # Cargamos la configuracion del cluster
    # TODO Cambiarlo para el cluster
    # config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")  # Cargamos la configuracion del cluster
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

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
