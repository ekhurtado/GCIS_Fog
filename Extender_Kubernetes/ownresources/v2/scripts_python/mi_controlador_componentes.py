from kubernetes import client, config, watch
import tipos
import datetime

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha1"
namespace = "default"
plural = "componentes"


def controlador():

	config.load_kube_config("/etc/rancher/k3s/k3s.yaml")  # Cargamos la configuracion del cluster

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

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        objeto = event['object']
        tipo = event['type']

        print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo,
              "Nombre del objeto: ", objeto['metadata']['name'])

        if tipo != 'DELETED':
            # Lógica para llevar el recurso al estado deseado.
            conciliar_spec_status(objeto, cliente)
        if tipo == 'DELETED':
            eliminar_despliegues(objeto, 1)
            # Lógica para borrar lo asociado al recurso.

    # listado=cliente.list_namespaced_custom_object(grupo,version,namespace,plural,pretty="true", watch="true")


    print("Despues del watcher.")

def conciliar_spec_status(objeto, cliente):

	# Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
	# Habria que chequear las replicas, las versiones...
	# De momento esta version solo va a mirar el numero de replicas.
	# Chequea si la aplicacion que ha generado el evento esta al día en .spec y .status

	cliente_despliegue = client.AppsV1Api()

	# Miro el spec.
	componente_deseado= cliente.get_namespaced_custom_object(grupo, version, namespace, plural, objeto['metadata']['name'])

	# Miro el status.
	componente_desplegado = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'])

	# Compruebo.

	# ESTO ES UNA PRUEBA HASTA QUE PUEDA ACCEDER AL STATUS
	rep = 1
	deployment_yaml = tipos.deployment(objeto, rep)
	cliente_despliegue.create_namespaced_deployment(namespace, deployment_yaml)


	#Busco el status del deployment.
	status_deployment = cliente_despliegue.read_namespaced_deployment_status(deployment_yaml['metadata']['name'], namespace)
	replicas_desplegadas = status_deployment.status.available_replicas

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
