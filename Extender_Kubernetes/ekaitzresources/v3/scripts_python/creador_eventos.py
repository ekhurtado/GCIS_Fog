import os

from kubernetes import client, config, watch

import tipos

grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

def main():
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace('Extender_Kubernetes\ekaitzresources', "")
    path = path.replace('\\v2\scripts_python', "")  # Se ha tenido que realizar de este modo ya que con la v daba error
    # path = path.replace("Extender_Kubernetes\ekaitzresources\v2\scripts_python", "")
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

    # TODO Cambiarlo para el cluster
    # TODO PARA AÑADIR LA COMPROBACION DE ESTAR EN EL CLUSTER O FUERA DE EL
    # if 'KUBERNETES_PORT' in os.environ:
    # 	config.load_incluster_config()
    # else:
    # 	config.load_kube_config()

    cliente = client.CustomObjectsApi()  # Creamos el cliente de la API


    print("Que evento de aplicacion quieres crear?")
    print("   -> CREAR")
    print("   -> ELIMINAR")
    print("   -> MODIFICAR")
    eventType = input()
    match str.upper(eventType):
        case "CREAR" | "CREATE":
            print("Formulario para crear aplicaciones... TODO")
        case "ELIMINAR" | "REMOVE" | "DELETE":
            print("Cuál es el nombre de la aplicacion a eliminar?\n")
            appName = input()
            cliente_evento = client.CoreV1Api()
            razon = 'DELETED'
            eventBody = tipos.evento(
                'Mensaje de la aplicacion:' + appName, razon,
                appName + '-' + razon, appName)
            # cliente_evento.create_namespaced_event("default", eventBody)
            cliente.delete_namespaced_custom_object(grupo, version, namespace, plural, appName)
            print("Aplicacion eliminada")

        case "MODIFICAR" | "MODIFY":
            print("Formulario para modificar aplicaciones... TODO")
        case _:
            print("Caso generico")

if __name__ == "__main__":
    main()