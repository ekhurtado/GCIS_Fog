import datetime
from kubernetes import config, watch
import mi_controlador_componentes
import tipos

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha1"
namespace = "default"
plural = "componentes"

def mi_watcher(cliente):

    config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    watcher=watch.Watch()

    print("Estoy en el watcher.") # Comprobacion por consola.

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo,
              "Nombre del objeto: ", objeto['metadata']['name'])

        if tipo != 'DELETED':
            # Lógica para llevar el recurso al estado deseado.
            mi_controlador_componentes.conciliar_spec_status(objeto, cliente)
        if tipo == 'DELETED':
            mi_controlador_componentes.eliminar_despliegues(objeto, 1)
            # Lógica para borrar lo asociado al recurso.

    # listado=cliente.list_namespaced_custom_object(grupo,version,namespace,plural,pretty="true", watch="true")


    print("Despues del watcher.")


# if __name__ == "__main__":
#     mi_watcher(cliente)