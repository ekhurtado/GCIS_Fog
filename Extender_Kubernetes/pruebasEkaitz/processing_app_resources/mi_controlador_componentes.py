import json
import os

import pytz
from dateutil import parser
from kubernetes import client, config, watch
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
	path = path.replace("Extender_Kubernetes\pruebasEkaitz\processing_app_resources", "")
	print(os.path.join(os.path.abspath(path), "k3s.yaml"))

	# config.load_kube_config("k3s.yaml")  # Cargamos la configuracion del cluster
	# TODO Cambiarlo para el cluster
	# config.load_kube_config("C:\\Users\\ekait\\PycharmProjects\\GCIS\\GCIS_Fog\\k3s.yaml")  # Cargamos la configuracion del cluster
	config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

	cliente = client.CustomObjectsApi()  # Creamos el cliente de la API

	cliente_extension = client.ApiextensionsV1Api() # Cliente para añadir el CRD.

	try:
		cliente_extension.create_custom_resource_definition(tipos.CRD_comp())
		print("He pasado la CRD. Compruebalo y pulsa una tecla para continuar.")
		input()
	except Exception:  # No distingue, como puedo distinguir?
		print("El CRD ya existe, pasando al watcher.")

	# print("Listado de aplicaciones desplegadas en el cluster.")
	# listado_aplicaciones=cliente.list_namespaced_custom_object(grupo,version,namespace,plural,pretty="true")
	# print(listado_aplicaciones)

	mi_watcher(cliente) # Activamos el watcher de recursos componente.


def mi_watcher(cliente):

    watcher=watch.Watch()

    print("Estoy en el watcher.") # Comprobacion por consola.
    startedTime = pytz.utc.localize(datetime.datetime.utcnow())

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        creationTimeZ = objeto['metadata']['creationTimestamp']
        creationTime = parser.isoparse(creationTimeZ)

        if creationTime < startedTime:
           print("El evento es anterior, se ha quedado obsoleto")  # TODO se podria mirar si añadir una comprobacion por si hay algun evento que no se ha gestionado
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
                # Lógica para llevar el recurso al estado deseado.
                conciliar_spec_status(objeto, cliente)

		# TODO se ha reformateado para no añadir tantos IFs
        # if tipo != 'DELETED':
        #     # Lógica para llevar el recurso al estado deseado.
        #     conciliar_spec_status(objeto, cliente)
        # if tipo == 'DELETED':
        #     eliminar_despliegues(objeto, 1)
        #     # Lógica para borrar lo asociado al recurso.

    # listado=cliente.list_namespaced_custom_object(grupo,version,namespace,plural,pretty="true", watch="true")


    print("Despues del watcher.")


def check_modifications(objeto, cliente):

	print("Algo se ha modificado")
	print(objeto)

def conciliar_spec_status(objeto, cliente):

	# Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
	# Habria que chequear las replicas, las versiones...
	# De momento esta version solo va a mirar el numero de replicas.
	# Chequea si la aplicacion que ha generado el evento esta al día en .spec y .status

	# TODO El componente ya se ha creado, ahora se va a desplegar. Por eso se va a actualizar el estado
	status_object = {'status': {'situation': 'Deploying'}}
	cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'], status_object)


	cliente_despliegue = client.AppsV1Api()

	# Miro el spec.
	componente_deseado= cliente.get_namespaced_custom_object(grupo, version, namespace, plural, objeto['metadata']['name'])

	# Miro el status.
	componente_desplegado = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'])

	# cluster_object = cliente.get_cluster_custom_object(grupo, version, plural, objeto['metadata']['name'])
	#
	# cluster_status = cliente.get_cluster_custom_object_status(grupo, version, plural, objeto['metadata']['name'])
	#
	# scale = cliente.get_namespaced_custom_object_scale(grupo, version, namespace, plural, objeto['metadata']['name'])
	#
	# cluster_scale = cliente.get_cluster_custom_object_scale(grupo, version, plural, objeto['metadata']['name'])

	# Compruebo.

	# ESTO ES UNA PRUEBA HASTA QUE PUEDA ACCEDER AL STATUS
	rep = 1
	deployment_yaml = tipos.deployment(objeto, rep)
	cliente_despliegue.create_namespaced_deployment(namespace, deployment_yaml)


	#Busco el status del deployment.
	status_deployment = cliente_despliegue.read_namespaced_deployment_status(deployment_yaml['metadata']['name'], namespace)
	replicas_desplegadas = status_deployment.status.available_replicas

	while replicas_desplegadas is None:	# hasta que no se haya desplegado, esperamos
		status_deployment = cliente_despliegue.read_namespaced_deployment_status(deployment_yaml['metadata']['name'],
																				 namespace)
		replicas_desplegadas = status_deployment.status.available_replicas
		# print(replicas_desplegadas)

	# TODO Intento de actualizar el status del componente
	# replicas_desplegadas = 1 # TODO borrar, es para ver si actualiza el status
	status_object = {'status': {'replicas': replicas_desplegadas, 'situation': 'Running'}}
	print(json.dumps(status_object))
	cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'], status_object)

	componente_actualizado = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'])

	print("Actualizacion de status finalizada")

	# TODO Prueba de captura de nombre de la aplicacion a la que pertenece
	myAppName = componente_desplegado['metadata']['labels']['applicationName']
	print("My application is: " + str(myAppName))

	# TODO Ahora hay que crear el status de cada componente en el custom resource de la aplicacion y que el componente lo actualice cuando se haya desplegado
	# 	para eso utilizará el nombre de su aplicacion y modificará su custom resource, creando un evento MODIFIED que pueda leer el controlador de aplicaciones

	# TODO Prueba para leer y actualizar el status de la aplicacion
	mi_aplicacion = cliente.get_namespaced_custom_object_status(grupo, version_aplicaciones, namespace, plural_aplicaciones,
																myAppName)
	for i in range(len(mi_aplicacion['status']['componentes'])):
		if (mi_aplicacion['status']['componentes'][i]['name'] == objeto['spec']['name']):
			mi_aplicacion['status']['componentes'][i]['status'] = "Running"
			cliente.patch_namespaced_custom_object_status(grupo, version_aplicaciones, namespace,
														  plural_aplicaciones, myAppName, {'status': mi_aplicacion['status']})
			break

	print(mi_aplicacion)


	# if componente_deseado['spec']['replicas'] != componente_desplegado['spec']['replicas']:
	# 	if componente_deseado['spec']['replicas'] > componente_desplegado['spec']['replicas']:
	# 		pass
	# 		# En caso de modificacion del numero de replicas o objeto recien añadido.
	# 		# Habria que desplegar las replicas restantes.
	# 		# for i in aplicacion_deseada['spec']['replicas'] - aplicacion_desplegada['status']['replicas']:
	# 		# 	desplegar_replica()
	# 	if componente_deseado['spec']['replicas'] < componente_desplegado['spec']['replicas']: # Actualizar a 'status' cuando pueda acceder
	# 		pass
	# 		# En caso de modificacion del numero de replicas.
	# 		# Habria que eliminar las replicas sobrantes.
	# 		# for i in aplicacion_deseada['status']['replicas'] - aplicacion_desplegada['spec']['replicas']:
	# 		# 	desplegar_replica()


def eliminar_despliegues(objeto, replicas):
	cliente_despliegue = client.AppsV1Api()
	cliente_despliegue.delete_namespaced_deployment(tipos.deployment(objeto , replicas)['metadata']['name'], namespace)


if __name__ == '__main__':
	controlador()
