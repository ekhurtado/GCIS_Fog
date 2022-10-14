from kubernetes import client, config
import tipos

grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

def pasar_a_ejecucion( nombre):
    config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    cliente = client.CustomObjectsApi()
    app=cliente.get_namespaced_custom_object(grupo, version, namespace, plural, nombre)
    if app['spec']['desplegar'] == False:
        app['spec']['desplegar'] = True
        cliente.patch_namespaced_custom_object(grupo, version, namespace, plural, nombre, app)
    else:
        pass

if __name__ == '__main__':
    pasar_a_ejecucion('aplicacion-solicitada-prueba')