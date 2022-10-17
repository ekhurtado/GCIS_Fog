from dateutil import parser
from kubernetes import client, config, watch
import datetime
import tipos

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

def pasar_a_ejecucion(nombre):
    job=tipos.job_pasar_a_ejecucion(nombre)
    cliente_batch=client.BatchV1Api()
    cliente_batch.create_namespaced_job(namespace, job)

def watcher_eventos(cliente):
    watcher = watch.Watch()
    startedTime = datetime.datetime.now(datetime.timezone.utc)

    for event in watcher.stream(cliente.list_event_for_all_namespaces):
        objeto = event['object']
        tipo = event['type']

        '''
        if objeto.last_timestamp is None and objeto.event_time is None and objeto.action != "REACCIONO":
            continue

        creationTime = objeto.last_timestamp
        if creationTime is None:
            creationTime = objeto.event_time
            # print(objeto)
            # print(creationTime)

        if creationTime < startedTime:
            print("El evento es anterior, se ha quedado obsoleto")  # TODO se podria mirar si añadir una comprobacion por si hay algun evento que no se ha gestionado
            continue
        '''

        print("Nuevo evento: ", "Hora del evento: ", objeto.first_timestamp, "Tipo de evento: ", tipo, "Motivo:", objeto.reason, "Mensaje:", objeto.message)
        if objeto.action== 'DESPLEGAR':
            pasar_a_ejecucion(objeto.involved_object.name)



def gestor():
    # config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    # TODO Cambiarlo para el cluster
    config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")

    watcher_eventos(client.CoreV1Api())

if __name__ == '__main__':
	gestor()