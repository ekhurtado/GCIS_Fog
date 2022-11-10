import os

from kubernetes import client, config
import tipos

grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

def pasar_a_ejecucion( nombre):

    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace("Extender_Kubernetes\\ownresources\\v2\\scripts_python", "")
    print(os.path.join(os.path.abspath(path), "k3s.yaml"))

    # config.load_kube_config("k3s.yaml")  # Cargamos la configuracion del cluster
    # TODO Cambiarlo para el cluster
    # config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")  # Cargamos la configuracion del cluster
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

    cliente = client.CustomObjectsApi()
    app=cliente.get_namespaced_custom_object(grupo, version, namespace, plural, nombre)
    if app['spec']['desplegar'] == False:
        app['spec']['desplegar'] = True
        cliente.patch_namespaced_custom_object(grupo, version, namespace, plural, nombre, app, field_manager="gestor-ejecuciones")
    else:
        pass

if __name__ == '__main__':
    pasar_a_ejecucion('aplicacion-solicitada-prueba1')