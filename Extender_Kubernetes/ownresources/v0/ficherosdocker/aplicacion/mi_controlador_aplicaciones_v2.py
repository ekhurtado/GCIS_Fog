from kubernetes import client, config
import mi_watcher_aplicaciones_v2 as mi_watcher_aplicaciones
import tipos

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha3"
namespace = "default"
plural = "aplicaciones"


def controlador():
	
	config.load_incluster_config()
	# config.load_kube_config("/etc/rancher/k3s/k3s.yaml")  # Cargamos la configuracion del cluster

	cliente = client.CustomObjectsApi()  # Creamos el cliente de la API

	cliente_extension = client.ApiextensionsV1Api() # Creamos el cliente que pueda implementar el CRD.

	try:
		cliente_extension.create_custom_resource_definition(tipos.CRD_app())
	#	print("He pasado la CRD. Compruebalo y pulsa una tecla para continuar.")
	#	input()
	except Exception: #No distingue, pero funciona, como puedo distinguir?
		pass
	#	print("El CRD ya existe, pasando al watcher.")

	mi_watcher_aplicaciones.mi_watcher(cliente) # Activo el watcher de recursos aplicacion.

def conciliar_spec_status(objeto, cliente):

	# Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
	# Habria que chequear las replicas, las versiones...
	# De momento esta version solo va a mirar el numero de replicas.
	# Chequea si la aplicacion que ha generado el evento esta al día en .spec y .status

	cliente_despliegue = client.AppsV1Api()

	# Miro el spec.
	aplicacion_deseada = cliente.get_namespaced_custom_object(grupo, version, namespace, plural, objeto['metadata']['name'])

	# Miro el status.
	aplicacion_desplegada = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural, objeto['metadata']['name'])

	# Compruebo.

	# ESTO ES UNA PRUEBA HASTA QUE PUEDA ACCEDER AL STATUS
	# print(a)
	# La aplicación crea los componentes que la forman.
	for i in objeto['spec']['componentes']:
		for j in range(objeto['spec']['replicas']): # No me convence el aplicar así las replicas
			componente = tipos.componente_recurso(i['name'] + '-' + str(j + 1) + '-' +objeto['metadata']['name'], i['image'], i['previous'], i['next'])
			# Creo que es mejor aplicar algún label a los componentes en función de que aplicación formen.
			# Si no distinguimos los nombres bien surge el problema de que los nombres de los componentes al solicitar dos aplicaciones colisionan.
			cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente)


	#Busco el status del deployment.
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


def eliminar_componentes(aplicacion): # Ya no borrará deployments.
	cliente=client.CustomObjectsApi()

	# Hace falta añadir que borre los componentes según número de replicas.
	for i in aplicacion['spec']['componentes']:
		for j in range(aplicacion['spec']['replicas']):
			a = i['name'] + '-' + str(j + 1) + '-' +aplicacion['metadata']['name']
			cliente.delete_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', tipos.componente_recurso(i['name'] + '-' + str(j + 1) + '-' +aplicacion['metadata']['name'], i['image'], i['previous'], i['next'])['metadata']['name'])

if __name__ == '__main__':
	controlador()
