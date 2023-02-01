import os

import pytz
from dateutil import parser
from kubernetes import client, config, watch
from kubernetes.client import V1PodSpec

import tipos
import datetime

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha1"
namespace = "default"
plural = "componentes"

# Parámetros de la configuracion de las aplicaciones
version_aplicaciones = "v1alpha4"
plural_aplicaciones = "aplicaciones"


# TODO Hay que ver que datos se repiten mucho y crear variables globales (como el nombre del componente (tambien es aplicable a las aplicaciones))

def controlador():
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace('Extender_Kubernetes\ekaitzresources', "")
    path = path.replace('\\v2\scripts_python', "")  # Se ha tenido que realizar de este modo ya que con la v daba error
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

    # TODO Cambiarlo para el cluster
    # if 'KUBERNETES_PORT' in os.environ:
    # 	config.load_incluster_config()
    # else:
    # 	config.load_kube_config()

    cliente = client.CustomObjectsApi()  # Creamos el cliente de la API
    cliente_extension = client.ApiextensionsV1Api()  # Cliente para añadir el CRD.

    try:
        cliente_extension.create_custom_resource_definition(tipos.CRD_comp())
        print("He pasado la CRD. Compruebalo y pulsa una tecla para continuar.")
        input()
    except Exception:  # No distingue, como puedo distinguir?
        print("El CRD ya existe, pasando al watcher.")

    mi_watcher(cliente)  # Activamos el watcher de recursos componente.


def mi_watcher(cliente):
    watcher = watch.Watch()

    print("Estoy en el watcher.")  # Comprobacion por consola.
    startedTime = pytz.utc.localize(datetime.datetime.utcnow())

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        creationTimeZ = objeto['metadata']['creationTimestamp']
        creationTime = parser.isoparse(creationTimeZ)

        if creationTime < startedTime:
            print(
                "El evento es anterior, se ha quedado obsoleto")  # TODO se podria mirar si añadir una comprobacion por si hay algun evento que no se ha gestionado
            continue

        print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo,
              "Nombre del objeto: ", objeto['metadata']['name'])

        match tipo:
            case "MODIFIED":
                # Logica para analizar que se ha modificado
                check_modifications(objeto, cliente)
            case "DELETED":
                eliminar_despliegues(objeto, 1)
                # Lógica para borrar lo asociado al recurso.
            case _:

                # Creamos el evento notificando que se ha creado el componente
                eventObject = tipos.customResourceEventObject(action='Creado', CR_type="componente",
                                                              CR_object=objeto,
                                                              message='Componente creado correctamente.',
                                                              reason='Created')
                eventAPI = client.CoreV1Api()
                eventAPI.create_namespaced_event("default", eventObject)

                # Lógica para llevar el recurso al estado deseado.
                conciliar_spec_status(objeto, cliente)

    print("Despues del watcher.")


def check_modifications(objeto, cliente):
    print("Algo se ha modificado")
    print(objeto)


def conciliar_spec_status(objeto, cliente):
    # Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
    # Habria que chequear las réplicas, las versiones...
    # De momento esta version solo va a mirar el número de réplicas.
    # Chequea si la aplicacion que ha generado el evento está al día en .spec y .status

    # TODO El componente ya se ha creado, ahora se va a desplegar. Por eso, se va a actualizar el estado
    status_object = {'status': {'situation': 'Deploying'}}
    cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'],
                                                  status_object)

    # Creamos el evento notificando que se está desplegando el componente
    eventAPI = client.CoreV1Api()
    eventObject = tipos.customResourceEventObject(action='Desplegando', CR_type="componente",
                                                  CR_object=objeto,
                                                  message='Iniciado despliegue de componente.',
                                                  reason='Deploying')
    eventAPI.create_namespaced_event("default", eventObject)

    cliente_despliegue = client.AppsV1Api()

    # Miro el spec.
    componente_deseado = cliente.get_namespaced_custom_object(grupo, version, namespace, plural,
                                                              objeto['metadata']['name'])

    # Miro el status.
    componente_desplegado = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                        objeto['metadata']['name'])

    # TODO Prueba de captura de nombre de la aplicacion a la que pertenece
    myAppName = componente_desplegado['metadata']['labels']['applicationName']
    shortName = componente_desplegado['metadata']['labels'][
        'shortName']  # este incluye el nombre original del componente
    print("My application is: " + str(myAppName))

    # ESTO ES UNA PRUEBA HASTA QUE PUEDA ACCEDER AL STATUS
    # rep = 1
    # deployment_yaml = tipos.deployment(objeto, rep)
    # cliente_despliegue.create_namespaced_deployment(namespace, deployment_yaml)

    # TODO Añadir los deployments personalizables de las aplicaciones de adquisicion y procesamiento
    if "permanente" in componente_deseado['spec']:
        deployment_yaml = tipos.deploymentObject(objeto, "component-controller", myAppName, 1,
                                                 # TODO De momento metemos a mano que solo se despliegue una replica
                                                 shortName, configMap=componente_deseado['spec']['permanenteCM'])
    else:
        deployment_yaml = tipos.deploymentObject(objeto, "component-controller", myAppName, 1,
                                                 # TODO De momento metemos a mano que solo se despliegue una replica
                                                 shortName)
    cliente_despliegue.create_namespaced_deployment(namespace, deployment_yaml)

    # Busco el status del deployment.
    status_deployment = cliente_despliegue.read_namespaced_deployment_status(deployment_yaml['metadata']['name'],
                                                                             namespace)
    replicas_desplegadas = status_deployment.status.available_replicas

    while replicas_desplegadas is None:  # hasta que no se haya desplegado, esperamos
        status_deployment = cliente_despliegue.read_namespaced_deployment_status(deployment_yaml['metadata']['name'],
                                                                                 namespace)
        replicas_desplegadas = status_deployment.status.available_replicas
    # print(replicas_desplegadas)

	# Creamos el evento notificando que se ha desplegado el componente
    eventObject = tipos.customResourceEventObject(action='Desplegado', CR_type="componente",
												  CR_object=objeto,
												  message='Componente desplegado correctamente.',
												  reason='Running')
    eventAPI.create_namespaced_event("default", eventObject)

    # Actualizamos el status del componente
    status_object = {'status': {'replicas': replicas_desplegadas, 'situation': 'Running'}}
    cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'],
                                                  status_object)
    print("Actualizacion de status finalizada")

    # Por último, se va a leer y actualizar el status de la aplicacion
    mi_aplicacion = cliente.get_namespaced_custom_object_status(grupo, version_aplicaciones, namespace,
                                                                plural_aplicaciones, myAppName)
    field_manager = 'componente-' + shortName + '-' + mi_aplicacion['metadata']['name']
    for i in range(len(mi_aplicacion['status']['componentes'])):
        if (mi_aplicacion['status']['componentes'][i]['name'] == objeto['spec']['name']):
            mi_aplicacion['status']['componentes'][i]['status'] = "Running"
            cliente.patch_namespaced_custom_object_status(grupo, version_aplicaciones, namespace,
                                                          plural_aplicaciones, myAppName,
                                                          {'status': mi_aplicacion['status']},
                                                          field_manager=field_manager)
            break

    print(mi_aplicacion)


def eliminar_despliegues(objeto, replicas):
    cliente_despliegue = client.AppsV1Api()
    cliente_despliegue.delete_namespaced_deployment(tipos.deployment(objeto, replicas)['metadata']['name'], namespace)


if __name__ == '__main__':
    controlador()
