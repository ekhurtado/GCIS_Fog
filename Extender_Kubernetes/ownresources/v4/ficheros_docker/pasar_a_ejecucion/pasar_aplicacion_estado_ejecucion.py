from kubernetes import client, config
import os

grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

def pasar_a_ejecucion():
    config.load_incluster_config()
    cliente = client.CustomObjectsApi()
    nombre=os.environ.get('NOMBRE_APP')
    app=cliente.get_namespaced_custom_object(grupo, version, namespace, plural, nombre)
    if app['spec']['desplegar'] == False:
        app['spec']['desplegar'] = True
        cliente.patch_namespaced_custom_object(grupo, version, namespace, plural, nombre, app)
    else:
        pass

if __name__ == '__main__':
    pasar_a_ejecucion()
