import logging
import os
import sys

import pytz
from kubernetes import client, config, watch
import datetime

path = os.path.abspath(os.path.dirname(__file__))
path = path.replace("Extender_Kubernetes\pruebasEkaitz", "")
print(os.path.join(os.path.abspath(path), "k3s.yaml"))

# config.load_kube_config("k3s.yaml")  # Cargamos la configuracion del cluster
# TODO Cambiarlo para el cluster
# config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")  # Cargamos la configuracion del cluster
config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

eventAPI = client.EventsV1Api()
coreAPI = client.CoreV1Api()
create_time = pytz.utc.localize(datetime.datetime.utcnow())

estructura_evento = {
    'api_Version': 'v1',
    'eventTime': create_time,
    'firstTimestamp' : create_time,
    'lastTimestamp' : create_time,
    'action': 'CREADO',
    'involvedObject': {  # probar tambien con related
        'apiVersion': 'misrecursos.aplicacion/v1alpha4',
        'kind': 'Aplicacion',
        'name': 'aplicacion-solicitada-prueba1',
        'namespace': 'default',
        'fieldPath': 'Events',  # No hace nada.
        'uid': '02556c7b-7a80-419e-aa7d-5f4bb6e44a69',
    },
    'kind': 'Event',
    'message': 'Aplicacion desplegada correctamente2',
    'reason': 'Created',
    'reportingComponent': 'controlador-externo',
    'reportingInstance': 'controlador-externo',
    'type': 'Normal',
    'metadata': {
        # 'name': 'evento-creado21',
        'creation_timestamp': create_time
    },
    'source': {
        'component': 'pruebaEventos.py3'
    }
}
# eventAPI.create_namespaced_event(namespace="default", body=estructura_evento)
# coreAPI.create_namespaced_event(self=None, namespace="default", body=estructura_evento)
coreAPI.create_namespaced_event("default", estructura_evento)
# eventAPI.create_namespaced_event("default", estructura_evento)
