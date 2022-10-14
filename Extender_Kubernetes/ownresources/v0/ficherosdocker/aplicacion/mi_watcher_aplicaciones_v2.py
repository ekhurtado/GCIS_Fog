import datetime
from kubernetes import config, watch
import mi_controlador_aplicaciones_v2 as mi_controlador_aplicaciones


# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha3"
namespace = "default"
plural = "aplicaciones"


def mi_watcher(cliente):

    config.load_incluster_config()
    #config.load_kube_config("/etc/rancher/k3s/k3s.yaml") # Cargo la configuración
    watcher=watch.Watch() # Activo el watcher.

    # print("Estoy en el watcher.") # Comprobación por consola.

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        # print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo, "Nombre del objeto: ", objeto['metadata']['name'])            

        if tipo != 'DELETED':
            # Lógica para llevar el recurso al estado deseado.
            mi_controlador_aplicaciones.conciliar_spec_status(objeto, cliente)
        if tipo == 'DELETED':
            mi_controlador_aplicaciones.eliminar_componentes(objeto)
            # Lógica para borrar lo asociado al recurso.

    # print("Despues del watcher.")
