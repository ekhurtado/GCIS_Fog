from kubernetes import client, config

import tipos
import sys

grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

# Comando para ejecutarlo:
# cd hasta la carpeta donde esta evento_simulado.py
# C:\Python310\python.exe .\evento_simulado.py aplicacion-solicitada-nuevaapp

def simular_evento():
    # config.load_kube_config('/etc/rancher/k3s/k3s.yaml')
    # TODO Cambiarlo para el cluster
    config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")

    cliente=client.CoreV1Api()
    nombre=sys.argv[1]
    print('Desplegando:' + nombre)
    evento=tipos.evento('Este es un evento simulado para poner en ejecucion una aplicacion.', 'AplicacionDesplegada', 'desplegar-app'+nombre, nombre)
    evento['action'] = 'DESPLEGAR'
    cliente.create_namespaced_event(namespace,evento)


if __name__ == '__main__':
    simular_evento()