import datetime
from kubernetes import client, config, watch
import mi_controlador_aplicaciones
import time

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha3"
namespace = "default"
plural = "aplicaciones"
# nombre = "aplicacion-de-prueba"

def mi_watcher(cliente):

    config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    # cliente=client.CustomObjectsApi()
    watcher=watch.Watch()

    print("Estoy en el watcher.")

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo,
              "Nombre del objeto: ", objeto['metadata']['name'])

        if tipo != 'DELETED':
            # Lógica para llevar el recurso al estado deseado.
            mi_controlador_aplicaciones.mostrar_datos(objeto['metadata']['name'], cliente)
            mi_controlador_aplicaciones.conciliar_spec_status(objeto['metadata']['name'], objeto['spec']['replicas'], cliente)
        if tipo == 'DELETED':
            mi_controlador_aplicaciones.eliminar_despliegues(objeto['metadata']['name'], objeto['spec']['replicas'])
            # Lógica para borrar lo asociado al recurso.

    # listado=cliente.list_namespaced_custom_object(grupo,version,namespace,plural,pretty="true", watch="true")


    print("Despues del watcher.")


# if __name__ == "__main__":
#     mi_watcher(cliente)