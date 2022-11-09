import logging
import os
import sys
import time

import urllib3.exceptions
from dateutil import parser
from kubernetes import client, config, watch
import tipos
import datetime
from datetime import timezone

import pytz

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"


# TODO si se quieren saber los atributos de un CRD 	> kubectl explain aplicacion --recursive=true


def controlador():
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace("Extender_Kubernetes\pruebasEkaitz\processing_app_resources", "")
    print(os.path.join(os.path.abspath(path), "k3s.yaml"))

    # config.load_kube_config("k3s.yaml")  # Cargamos la configuracion del cluster
    # TODO Cambiarlo para el cluster
    # config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")  # Cargamos la configuracion del cluster
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

    # TODO PARA AÑADIR LA COMPROBACION DE ESTAR EN EL CLUSTER O FUERA DE EL
    # if 'KUBERNETES_PORT' in os.environ:
    # 	config.load_incluster_config()
    # else:
    # 	config.load_kube_config()

    cliente = client.CustomObjectsApi()  # Creamos el cliente de la API

    cliente_extension = client.ApiextensionsV1Api()  # Creamos el cliente que pueda implementar el CRD.

    # TODO Hay que actualizar esta parte en el proyecto de Julen
    try:
        cliente_extension.create_custom_resource_definition(tipos.CRD_app())
        print("Se ha creado la CRD de las aplicaciones. Compruebalo y pulsa una tecla para continuar.")
        input()
    except urllib3.exceptions.MaxRetryError as e:
        print("ERROR DE CONEXION!")
        print("Es posible que la dirección IP del master en el archivo k3s.yaml no sea la correcta")
        controlador()
    except Exception as e:  # No distingue, pero funciona, como puedo distinguir?
        print(str(e))  # Si se quiere

        if "Reason: Conflict" in str(e):
            print("El CRD ya existe, pasando al watcher.")
        elif "No such file or directory" in str(e):
            print((
                      "No se ha podido encontrar el archivo YAML con la definicion de las aplicaciones. Revisa que todo esta correcto."))
            sys.exit()  # en este caso cierro el programa porque si no se reinicia todo el rato
        # TODO Cuidado al meterlo en un contenedor, no hay que parar el programa ya que se quedaria sin funcionalidad

    mi_watcher(cliente)  # Activo el watcher de recursos aplicacion.


def mi_watcher(cliente):
    watcher = watch.Watch()  # Activo el watcher.
    print('Estoy en el watcher.')
    startedTime = pytz.utc.localize(
        datetime.datetime.utcnow())  # TODO CUIDADO! En el contenedor habria que instalar pytz

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        print('He detectado un evento.')
        objeto = event['object']
        tipo = event['type']

        a = cliente.get_namespaced_custom_object(grupo, version, namespace, plural, objeto['metadata']['name'])
        b = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'])

        creationTimeZ = objeto['metadata']['creationTimestamp']
        creationTime = parser.isoparse(creationTimeZ)

        if creationTime < startedTime:
            print(
                "El evento es anterior, se ha quedado obsoleto")  # TODO se podria mirar si añadir una comprobacion por si hay algun evento que no se ha gestionado
            continue

        print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo,
              "Nombre del objeto: ", objeto['metadata']['name'])

        # TODO Creamos el evento notificando que se ha creado la aplicacion
        eventObject = tipos.customResourceEventObject(action='Creado', CR_type="aplicacion",
                                                      CR_name=objeto['metadata']['name'],
                                                      CR_UID=objeto['metadata']['uid'],
                                                      message='Aplicacion creada correctamente.',
                                                      reason='Created',
                                                      eventName=objeto['metadata']['name'] + '-app-creada')
        eventAPI = client.CoreV1Api()
        eventAPI.create_namespaced_event("default", eventObject)


        match tipo:
            case "MODIFIED":
                # Logica para analizar que se ha modificado
                check_modifications(objeto, cliente)
            case "DELETED":
                eliminar_componentes(objeto)
                # Lógica para borrar lo asociado al recurso.
            case _:  # default case
                # Lógica para llevar el recurso al estado deseado.
                conciliar_spec_status(objeto, cliente)

        # elif tipo != 'DELETED':
        #     # Lógica para llevar el recurso al estado deseado.
        #     conciliar_spec_status(objeto, cliente)
        # elif tipo == 'DELETED':
        #     eliminar_componentes(objeto)
        #     # Lógica para borrar lo asociado al recurso.


def check_modifications(objeto, cliente):
    print("Algo se ha modificado")
    print(objeto)

    # TODO Analizar quien ha realizado el ultimo cambio (el parametro field_manager del metodo patch)
    if "componente" in objeto['metadata']['managedFields'][len(objeto['metadata']['managedFields']) - 1]['manager']:
        # Solo si ha actualizado el status un componente realizamos las comprobaciones
        print("Cambio realizado por un componente")

        # TODO IDEA: El atributo READY es un String ("current/desired")-> comprobar los componentes que estan en running e ir actualizando el current
        #  	Kubernetes no tiene un tipo de datos para hacer el ready 1/3, asi que hay que hacerlo con strings

        runningCount = 0
        for i in range(len(objeto['status']['componentes'])):
            if (objeto['status']['componentes'][i][
                'status'] == "Running"):  # TODO CUIDADO! Si se añaden replicas habria que comprobar que todas las replicas esten en Running
                # readyComponents = objeto['status']['ready'].split("/")[0]
                # readyNumComponents = int(readyComponents) + 1
                # objeto['status']['ready'] = str(readyNumComponents) + "/" + objeto['status']['ready'].split("/")[1]
                runningCount = runningCount + 1
        # else:
        # 	notRunningCount = notRunningCount + 1	# Si encuentra alguno que no está en Running, toda la aplicacion no esta desplegada

        if runningCount != 0:  # Algun componente esta en Running
            objeto['status']['ready'] = str(runningCount) + "/" + objeto['status']['ready'].split("/")[1]

            if runningCount == len(
                    objeto['status']['componentes']):  # Significa que todos los componentes esta en running
                currentReplicas = objeto['status']['replicas']
                # objeto['status']['replicas'] = int(currentReplicas) + 1
                objeto['status']['replicas'] = objeto['spec']['replicas']

            # Finalmente, actualizamos el objeto
            field_manager = objeto['metadata']['name']
            cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                          objeto['metadata']['name'], {'status': objeto['status']},
                                                          field_manager=field_manager)
        # cliente.replace_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'], {'status': objeto['status']})
    else:
        print("Cambio realizado por una aplicacion")


def conciliar_spec_status(objeto, cliente):
    # Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
    # Habria que chequear las replicas, las versiones...
    # De momento esta version solo va a mirar el numero de replicas.
    # Chequea si la aplicacion que ha generado el evento esta al día en .spec y .status

    cliente_despliegue = client.AppsV1Api()

    # Miro el spec.
    aplicacion_deseada = cliente.get_namespaced_custom_object(grupo, version, namespace, plural,
                                                              objeto['metadata']['name'])

    # Miro el status.
    aplicacion_desplegada = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                        objeto['metadata']['name'])

    # Compruebo.

    # ESTO ES UNA PRUEBA HASTA QUE PUEDA ACCEDER AL STATUS
    # print(a)
    # La aplicación crea los componentes que la forman.

    # TODO Creamos el evento de que se están empezando a crear los componentes

    if objeto['spec']['desplegar'] == True:
        listado_componentes_desplegados = cliente.list_namespaced_custom_object(grupo, 'v1alpha1', namespace,
                                                                                'componentes')
        for i in objeto['spec']['componentes']:  # Por cada componente de la aplicacion a desplegar
            permanente = False
            try:
                permanente = i['permanente']
            except KeyError:
                pass
            if (
                    permanente != True):  # Si el componente de la aplicacion esta marcado como permanente y es alguno de los componentes ya desplegados en el cluster y marcado como permanente.
                crear_componentes(cliente, i, objeto)
            else:
                encontrado = False
                for h in listado_componentes_desplegados['items']:  # Por cada componente desplegado en el cluster
                    if ('componente-' + i['name']) == h['metadata']['name']:
                        encontrado = True
                if encontrado:
                    pass
                else:
                    crear_componentes(cliente, i, objeto)



    elif objeto['spec']['desplegar'] == False:
        pass


# Busco el status del deployment.
# status_deployment = cliente_despliegue.read_namespaced_deployment_status(deployment_yaml['metadata']['name'], namespace)
# replicas_desplegadas = status_deployment.status.available_replicas

# if aplicacion_deseada['spec']['replicas'] != aplicacion_desplegada['spec']['replicas']:
# 	if aplicacion_deseada['spec']['replicas'] > aplicacion_desplegada['spec']['replicas']:
# 		pass
# 		# En caso de modificacion del numero de replicas o objeto recien añadido.
# 		# Habria que desplegar las replicas restantes.
# 		# for i in aplicacion_deseada['spec']['replicas'] - aplicacion_desplegada['status']['replicas']:
# 		# 	desplegar_replica()
# 	if aplicacion_deseada['spec']['replicas'] < aplicacion_desplegada['spec']['replicas']: # Actualizar a 'status' cuando pueda acceder
# 		pass
# 		# En caso de modificacion del numero de replicas.
# 		# Habria que eliminar las replicas sobrantes.
# 		# for i in aplicacion_deseada['status']['replicas'] - aplicacion_desplegada['spec']['replicas']:
# 		# 	desplegar_replica()

def crear_componentes(cliente, componente, app):
    # TODO Primero añadiremos el status en el CR de aplicacion para notificar que sus componentes se estan creando
    #  para ello, tendremos que analizar cuantos componentes tiene la aplicacion para crear el objeto status
    num_componentes = len(app['spec']['componentes'])
    status_object = {'status': {'componentes': [0] * num_componentes, 'replicas': 0,
                                'ready': "0/" + str(num_componentes)}}  # las replicas en este punto están a 0
    for i in range(int(num_componentes)):
        status_object['status']['componentes'][i] = {'name': app['spec']['componentes'][i]['name'],
                                                     'status': "Creating"}
    cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                  app['metadata']['name'], status_object)

    for j in range(app['spec']['replicas']):  # No me convence el aplicar así las replicas
        permanente = False
        try:
            permanente = componente['permanente']
        except KeyError:
            pass
        if permanente == True:  # En este if se repiten muchos comandos (la linea de crear el objeto, actualizar status...), arreglarlo
            componente_body = tipos.componente_recurso(componente['name'],
                                                       componente['image'],
                                                       componente['previous'],
                                                       app['metadata']['name'],
                                                       componente['next'], Permanente=True)
            cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente_body)

            break
        else:
            componente_body = tipos.componente_recurso(
                componente['name'] + '-' + str(j + 1) + '-' + app['metadata']['name'],
                componente['image'], componente['previous'], componente['next'], app['metadata']['name'])
            cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente_body)

        # Creo que es mejor aplicar algún label a los componentes en función de que aplicación formen.
        # Si no distinguimos los nombres bien surge el problema de que los nombres de los componentes al solicitar dos aplicaciones colisionan.

        # TODO Una vez creado el Custom Resource, vamos a añadirle el status de que se están creando los componentes
        status_object = {'status': {'replicas': 0, 'situation': 'Creating'}}
        cliente.patch_namespaced_custom_object_status(grupo, 'v1alpha1', namespace, 'componentes',
                                                      componente_body['metadata']['name'], status_object)


# TODO CONSEGUIR AÑADIR LA INFORMACION DEL NOMBRE DE LA APLICACION EN EL METADATA DE LOS COMPONENTES (para que sepan a que aplicacion pertenecen)


def eliminar_componentes(aplicacion):  # Ya no borrará deployments.
    cliente = client.CustomObjectsApi()

    if aplicacion['spec']['desplegar'] == True:
        for i in aplicacion['spec']['componentes']:
            permanente = False
            try:
                permanente = i['permanente']
            except KeyError:
                pass
            if permanente != True:
                for j in range(aplicacion['spec']['replicas']):
                    a = i['name'] + '-' + str(j + 1) + '-' + aplicacion['metadata']['name']
                    cliente.delete_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes',
                                                            tipos.componente_recurso(
                                                                i['name'] + '-' + str(j + 1) + '-' +
                                                                aplicacion['metadata']['name'], i['image'],
                                                                i['previous'], i['next'])['metadata']['name'])
    elif aplicacion['spec']['desplegar'] == False:
        pass


if __name__ == '__main__':
    controlador()
