from kubernetes import client, config, watch
import tipos
import os

# Obtención de los parámetros de configuración de los niveles actual e inferior.
# Nivel_Actual = os.environ['LevelName']
# Nivel_Siguiente = os.environ['NextLevelName']

#Falta implementar los plurales.

Nivel_Actual = 'activo'
Nivel_Siguiente = 'aplicacion'

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha1"
namespace = "default"
plural = Nivel_Actual + 's'


def controlador():
    # config.load_incluster_config()  # Cargamos la configuracion del cluster
    config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
    cliente = client.CustomObjectsApi()  # Creamos el cliente de la API

    mi_watcher(cliente)  # Activo el watcher de recursos de este nivel.


def mi_watcher(cliente):
    watcher = watch.Watch()  # Activo el watcher.

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        if tipo != 'DELETED':
            # Lógica para llevar el recurso al estado deseado.
            conciliar_spec_status(objeto, cliente)
        if tipo == 'DELETED':
            eliminar_recursos_nivel_inferior(objeto)
            # Lógica para borrar lo asociado al recurso.


def conciliar_spec_status(objeto, cliente):
    # Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
    # Habria que chequear las replicas, las versiones...
    # De momento esta version solo va a mirar el numero de replicas.
    # Chequea si la aplicacion que ha generado el evento esta al día en .spec y .status

    # if objeto['spec']['desplegar'] == True:
    #     for i in objeto['spec'][Nivel_Siguiente + 's']:  # Por cada recurso de nivel ingerior a desplegar.
    #         crear_recursos_nivel_inferior(cliente, i, objeto)
    # elif objeto['spec']['desplegar'] == False:
    #     pass


    for i in objeto['spec'][Nivel_Siguiente + 's']:  # Por cada recurso de nivel ingerior a desplegar.
        crear_recursos_nivel_inferior(cliente, i, objeto)


def crear_recursos_nivel_inferior(cliente, recurso_inferior, recurso):

    recurso_inferior['name']= recurso['spec']['name']+'-'+recurso_inferior['name']

    # for j in range(recurso['spec']['replicas']):  # No me convence el aplicar así las replicas
    #     permanente = False
    #     try:
    #         permanente = recurso_inferior['permanente']
    #     except KeyError:
    #         pass
    #     if permanente == True:
    #         Recurso_Nivel_Siguiente = tipos.Nivel_Siguiente(recurso_inferior['name'],
    #                                                    recurso_inferior['image'],
    #                                                    recurso_inferior['previous'],
    #                                                    recurso_inferior['next'], Permanente=True)
    #         cliente.create_namespaced_custom_object(grupo, version, namespace, Nivel_Siguiente + 's', Recurso_Nivel_Siguiente)
    #         break
    #     else:
    #         Recurso_Nivel_Siguiente = tipos.Nivel_Siguiente(
    #             recurso_inferior['name'] + '-' + str(j + 1) + '-' + recurso['metadata']['name'], recurso_inferior['image'],
    #             recurso_inferior['previous'], recurso_inferior['next'])
    #         cliente.create_namespaced_custom_object(grupo, version, namespace, Nivel_Siguiente + 's', Recurso_Nivel_Siguiente)
    # # Creo que es mejor aplicar algún label a los componentes en función de que aplicación formen.
    # # Si no distinguimos los nombres bien surge el problema de que los nombres de los componentes al solicitar dos aplicaciones colisionan.

    if recurso_inferior['desplegar'] == True:
        if Nivel_Siguiente == 'aplicacion':
            version_inf = 'v1alpha4'
            cliente.create_namespaced_custom_object(grupo, version_inf, namespace, Nivel_Siguiente + 'es',
                                                    tipos.recurso(recurso_inferior, Nivel_Siguiente))
        else:
            version_inf = 'v1alpha1'
            cliente.create_namespaced_custom_object(grupo, version_inf, namespace, Nivel_Siguiente + 's',
                                                    tipos.recurso(recurso_inferior, Nivel_Siguiente))

    elif recurso_inferior['desplegar'] == False:
        pass

def eliminar_recursos_nivel_inferior(recurso):  # Ya no borrará deployments.

    cliente = client.CustomObjectsApi()

    if recurso['spec']['desplegar'] == True:
        for i in recurso['spec'][Nivel_Siguiente + 's']:
            i['name']= recurso['spec']['name']+'-'+i['name']
            a=tipos.recurso(i, Nivel_Siguiente)
            if Nivel_Siguiente == 'aplicacion':
                cliente.delete_namespaced_custom_object(grupo, 'v1alpha4', namespace, Nivel_Siguiente + 'es',i['name'])
            else:
                cliente.delete_namespaced_custom_object(grupo, 'v1alpha1', namespace, Nivel_Siguiente + 's', i['name'])
    elif recurso['spec']['desplegar'] == False:
        pass


if __name__ == '__main__':
    controlador()
