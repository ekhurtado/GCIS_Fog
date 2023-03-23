from kubernetes import client, config, watch
import tipos
import os

# Libreria para pluralizar palabras en diversos idiomas
from inflector import Inflector, English, Spanish

# Obtención de los parámetros de configuración de los niveles actual e inferior.
# Nivel_Actual = os.environ['LevelName']
# Nivel_Siguiente = os.environ['NextLevelName']

# Falta implementar los plurales.

Nivel_Actual = os.environ.get('LEVEL_NAME')
Nivel_Siguiente = os.environ.get('NEXT_LEVEL_NAME')

# Parámetros de la configuración del objeto
grupo = "ehu.gcis.org"
version = "v1alpha1"
namespace = "default"
plural = os.environ.get('LEVEL_NAME_PLURAL')


def controlador():
    # config.load_incluster_config() # Cargamos la configuracion del cluster
    # config.load_kube_config("/etc/rancher/k3s/k3s.yaml")

    # TODO Cambiarlo para el cluster
    if 'KUBERNETES_PORT' in os.environ:
        config.load_incluster_config()
    else:
        config.load_kube_config()

    cliente = client.CustomObjectsApi()  # Creamos el cliente de la API

    mi_watcher(cliente)  # Activo el watcher de recursos de este nivel.


def mi_watcher(cliente):
    watcher = watch.Watch()  # Activo el watcher.

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        match tipo:
            case 'DELETED':
                eliminar_recursos_nivel_inferior(objeto)
                # Lógica para borrar lo asociado al recurso.
            case _:  # default case

                # TODO Creamos el evento notificando que se ha creado el recurso
                eventObject = tipos.customResourceEventObject(action='Created', CR_type=Nivel_Actual,
                                                              CR_object=objeto,
                                                              message=Nivel_Actual + ' successfully created.',
                                                              reason='Created')
                eventAPI = client.CoreV1Api()
                eventAPI.create_namespaced_event("default", eventObject)

                # Lógica para llevar el recurso al estado deseado.
                conciliar_spec_status(objeto, cliente)


def conciliar_spec_status(objeto, cliente):
    # Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
    # Habria que chequear las replicas, las versiones...
    # De momento esta version solo va a mirar el numero de replicas.
    # Chequea si la aplicacion que ha generado el evento esta al día en .spec y .status

    # if objeto['spec']['desplegar'] == True:
    #     for i in objeto['spec'][Nivel_Siguiente + 's']:  # Por cada recurso de nivel inferior a desplegar.
    #         crear_recursos_nivel_inferior(cliente, i, objeto)
    # elif objeto['spec']['desplegar'] == False:
    #     pass

    for i in objeto['spec'][Nivel_Siguiente + 's']:  # Por cada recurso de nivel ingerior a desplegar.
        crear_recursos_nivel_inferior(cliente, i, objeto)


def crear_recursos_nivel_inferior(cliente, recurso_inferior, recurso):
    recurso_inferior['name'] = recurso['spec']['name'] + '-' + recurso_inferior['name']

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

    if recurso_inferior['desplegar']:
        if Nivel_Siguiente == 'application':
            version_inf = 'v1alpha4'
        else:
            version_inf = 'v1alpha1'
        inflector_en = Inflector(English)
        cliente.create_namespaced_custom_object(grupo, version_inf, namespace, inflector_en.pluralize(Nivel_Siguiente),
                                                tipos.recurso(grupo, recurso_inferior, Nivel_Siguiente, version_inf))

        # TODO Creamos el evento notificando que se ha creado el recurso
        eventObject = tipos.customResourceEventObject(action='Created', CR_type=Nivel_Actual,
                                                      CR_object=recurso,
                                                      message=Nivel_Siguiente + ' successfully created by '
                                                                                + Nivel_Actual + '.',
                                                      reason='Created')
        eventAPI = client.CoreV1Api()
        eventAPI.create_namespaced_event("default", eventObject)

    elif not recurso_inferior['desplegar']:
        pass


def eliminar_recursos_nivel_inferior(recurso):  # Ya no borrará deployments.

    cliente = client.CustomObjectsApi()

    if recurso['spec']['desplegar']:
        for i in recurso['spec'][Nivel_Siguiente + 's']:
            i['name'] = recurso['spec']['name'] + '-' + i['name']
            a = tipos.recurso(grupo, i, Nivel_Siguiente)
            if Nivel_Siguiente == 'application':
                version_inf = 'v1alpha4'
            else:
                version_inf = 'v1alpha1'
            inflector_en = Inflector(English)
            cliente.delete_namespaced_custom_object(grupo, version_inf, namespace, inflector_en.pluralize(Nivel_Siguiente),
                                                    i['name'])
    elif not recurso['spec']['desplegar']:
        pass


if __name__ == '__main__':
    controlador()
