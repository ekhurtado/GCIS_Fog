from kubernetes import client, config, watch
import tipos
import os

# Libreria para pluralizar palabras en diversos idiomas (DE MOMENTO NO HACE FALTA)
# from inflector import Inflector, English, Spanish

# Obtención de los parámetros de configuración de los niveles actual, superior e inferior.

Nivel_Actual = os.environ.get('LEVEL_NAME')
Nivel_Actual_plural = os.environ.get('LEVEL_NAME_PLURAL')

Nivel_Inferior = os.environ.get('LOWER_LEVEL_NAME')
Nivel_Inferior_plural = os.environ.get('LOWER_LEVEL_NAME_PLURAL')

Nivel_Superior = os.environ.get('HIGHER_LEVEL_NAME')
Nivel_Superior_plural = os.environ.get('HIGHER_LEVEL_NAME_PLURAL')

# Parámetros de la configuración del objeto
grupo = "ehu.gcis.org"
version = "v1alpha1"
namespace = "default"
plural = Nivel_Actual_plural


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
            case "MODIFIED":
                # Logica para analizar que se ha modificado
                check_modifications(objeto, cliente)
            case 'DELETED':
                eliminar_recursos_nivel_inferior(objeto)
                # Lógica para borrar lo asociado al recurso.
            case _:  # default case

                # Creamos el evento asociado a la creacion del recurso
                createCreationRelatedEvent(objeto)

                # Generamos el objeto status en el recurso recien creado
                createStatus(objeto, cliente)

                # Lógica para llevar el recurso al estado deseado.
                conciliar_spec_status(objeto, cliente)


def check_modifications(objeto, cliente):
    print("El recurso " + objeto['metadata']['name'] + " se ha modificado")

    # Objeto para la API de los eventos
    eventAPI = client.CoreV1Api()

    # Primero analizamos quien ha realizado el ultimo cambio (el parametro field_manager del metodo patch)
    lastManager = objeto['metadata']['managedFields'][len(objeto['metadata']['managedFields']) - 1]['manager']
    if Nivel_Inferior in lastManager:
        # Solo si ha actualizado el status un recurso de nivel inferior realizamos las comprobaciones de posible cambio
        #   en el estado de los recursos inferiores

        # Conseguimos el nombre del componente del string del manager
        lowerResourceName = lastManager.replace(Nivel_Inferior + '-', '')  # le quitamos el tipo de recurso inferior
        lowerResourceName = lowerResourceName.replace('-' + objeto['metadata']['name'], '')  # le quitamos el ID
                                                                                             #   del recurso propio
        print("Cambio realizado por el recurso inferior: " + lowerResourceName)

        # Volvemos a conseguir el objeto del recurso propio por si se ha modificado
        updatedObject = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                    objeto['metadata']['name'])

        runningCount = 0
        for i in range(len(objeto['status'][Nivel_Inferior_plural])):
            # Recorremos el estado de todos los recursos inferiores analizando cuales estan desplegados
            if objeto['status'][Nivel_Inferior_plural][i]['status'] == "Running":
                runningCount = runningCount + 1

                if objeto['status'][Nivel_Inferior_plural][i]['name'] == lowerResourceName:
                    # Si el componente que ha enviado el mensaje es el que se ha pasasdo a estado Running,
                    # creamos el evento notificándolo tambien en este nivel
                    eventObject = tipos.customResourceEventObject(action='Deploying', CR_type=Nivel_Actual,
                                                      CR_object=objeto,
                                                      message=lowerResourceName + ' resource successfully deployed.',
                                                      reason='Deployed', )
                    eventAPI.create_namespaced_event("default", eventObject)

        if runningCount != 0:  # Si despues de analizar todos hay algún recurso que está en Running
            objeto['status']['ready'] = str(runningCount) + "/" + objeto['status']['ready'].split("/")[1]

            if runningCount == len(objeto['status'][Nivel_Inferior_plural]):
                # En este caso, significa que todos los recursos inferiores están en running
                # Creamos el evento notificandolo
                eventObject = tipos.customResourceEventObject(action='Running', CR_type=Nivel_Actual,
                                                              CR_object=objeto,
                                                              message='All lower resources successfully deployed.',
                                                              reason='Running')
                eventAPI.create_namespaced_event("default", eventObject)
                # También avisaremos al nivel superior de que este recurso ya está desplegado
                # Actualizamos la informacion en el recurso de nivel superior, indicando el estado del propio recurso
                patchCreationStatusToParent(objeto, cliente)

            # Finalmente, actualizamos el objeto con el nuevo status
            field_manager = objeto['metadata']['name']
            cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                          objeto['metadata']['name'], {'status': objeto['status']},
                                                          field_manager=field_manager)
    else:
        print("Cambio realizado por otro recurso")


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

    for i in objeto['spec'][Nivel_Inferior + 's']:  # Por cada recurso de nivel ingerior a desplegar.
        crear_recursos_nivel_inferior(cliente, i, objeto)


def crear_recursos_nivel_inferior(cliente, recurso_inferior, recurso):
    if recurso_inferior['deploy']:
        if Nivel_Inferior == 'application':
            version_inf = 'v1alpha4'
        else:
            version_inf = 'v1alpha1'

        # Generamos el ID del recurso inferior a partir de los niveles anteriores y el suyo
        recurso_inferior_ID = recurso['spec']['name'] + '-' + recurso_inferior['name']

        # Añadimos en el recurso inferior el nombre del recurso que lo ha creado
        recursoID = recurso['metadata']['name']

        cliente.create_namespaced_custom_object(grupo, version_inf, namespace, Nivel_Inferior_plural,
                                                tipos.recurso(grupo, recurso_inferior, Nivel_Inferior, version_inf,
                                                              recursoID, recurso_inferior_ID))

        # TODO Creamos el evento notificando que se ha creado el recurso
        eventObject = tipos.customResourceEventObject(action='Created', CR_type=Nivel_Actual,
                                                      CR_object=recurso,
                                                      message=Nivel_Inferior + ' successfully created by '
                                                              + Nivel_Actual + '.',
                                                      reason='Created')
        eventAPI = client.CoreV1Api()
        eventAPI.create_namespaced_event("default", eventObject)

    elif not recurso_inferior['desplegar']:
        pass


def eliminar_recursos_nivel_inferior(recurso):  # Ya no borrará deployments.

    cliente = client.CustomObjectsApi()

    if recurso['spec']['deploy']:
        for i in recurso['spec'][Nivel_Inferior + 's']:
            i['name'] = recurso['spec']['name'] + '-' + i['name']
            a = tipos.recurso(grupo, i, Nivel_Inferior)
            if Nivel_Inferior == 'application':
                version_inf = 'v1alpha4'
            else:
                version_inf = 'v1alpha1'

            cliente.delete_namespaced_custom_object(grupo, version_inf, namespace, Nivel_Inferior_plural,
                                                    i['name'])
    elif not recurso['spec']['deploy']:
        pass


def createCreationRelatedEvent(objeto):
    # TODO Creamos el evento notificando que se ha creado el recurso
    eventObject = tipos.customResourceEventObject(action='Created', CR_type=Nivel_Actual,
                                                  CR_object=objeto,
                                                  message=Nivel_Actual + ' successfully created.',
                                                  reason='Created')
    eventAPI = client.CoreV1Api()
    eventAPI.create_namespaced_event("default", eventObject)


def createStatus(objeto, cliente):
    # Primero añadiremos el status en el CR del recurso para notificar que sus recursos inferiores se están creando.
    #       Para ello, tendremos que analizar cuantos recursos inferiores tiene para crear el objeto status
    num_recursos_inferiores = len(objeto['spec'][Nivel_Inferior_plural])
    status_object = {'status': {Nivel_Inferior_plural: [0] * num_recursos_inferiores,
                                'ready': "0/" + str(num_recursos_inferiores)}}
    for i in range(int(num_recursos_inferiores)):
        status_object['status'][Nivel_Inferior_plural][i] = {'name': objeto['spec'][Nivel_Inferior_plural][i]['name'],
                                                             'status': "Deploying"}
    cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                  objeto['metadata']['name'], status_object)


def patchCreationStatusToParent(objeto, cliente):
    # Tambien avisamos al nivel superior de que el recurso se ha creado, añadiendolo en el status del
    #       recurso superior. En el nivel mas superior, como su padre es el sistema, no realiza esta acción

    if Nivel_Superior != 'system':
        # Primero, conseguimos el ID del recurso de nivel superior
        higher_level_resourceID = objeto['metadata']['labels']['parentID']

        parent_resource = cliente.get_namespaced_custom_object_status(grupo, version, namespace,
                                                                      Nivel_Superior_plural,
                                                                      higher_level_resourceID)
        field_manager = Nivel_Actual + '-' + objeto['metadata']['name'] + '-' + higher_level_resourceID
        for i in range(len(parent_resource['status'][Nivel_Actual_plural])):
            # buscamos entre los recursos el propio
            if parent_resource['status'][Nivel_Actual_plural][i]['name'] == objeto['spec']['name']:
                parent_resource['status'][Nivel_Actual_plural][i]['status'] = "Running"
                # Una vez localizado el recurso, actualizamos el status del recurso de nivel superior
                cliente.patch_namespaced_custom_object_status(grupo, version, namespace,
                                                              Nivel_Superior_plural, higher_level_resourceID,
                                                              {'status': parent_resource['status']},
                                                              field_manager=field_manager)


if __name__ == '__main__':
    controlador()
