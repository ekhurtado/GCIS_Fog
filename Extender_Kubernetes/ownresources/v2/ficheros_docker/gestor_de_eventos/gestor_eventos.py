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
    for event in watcher.stream(cliente.list_event_for_all_namespaces):
        objeto = event['object']
        tipo = event['type']
        print("Nuevo evento: ", "Hora del evento: ", objeto.first_timestamp, "Tipo de evento: ", tipo, "Motivo:", objeto.reason, "Mensaje:", objeto.message)
        if objeto.action== 'DESPLEGAR':
            pasar_a_ejecucion(objeto.involved_object.name)



def gestor():
    # config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    config.load_incluster_config()
    watcher_eventos(client.CoreV1Api())

if __name__ == '__main__':
	gestor()
