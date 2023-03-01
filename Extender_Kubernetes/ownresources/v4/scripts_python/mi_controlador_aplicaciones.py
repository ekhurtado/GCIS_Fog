from kubernetes import client, config, watch
import tipos
import datetime

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"


def controlador():

	config.load_kube_config("/etc/rancher/k3s/k3s.yaml")  # Cargamos la configuracion del cluster

	cliente = client.CustomObjectsApi()  # Creamos el cliente de la API

	cliente_extension = client.ApiextensionsV1Api() # Creamos el cliente que pueda implementar el CRD.

	try:
		cliente_extension.create_custom_resource_definition(tipos.CRD_app())
		print("He pasado la CRD. Compruebalo y pulsa una tecla para continuar.")
		input()
	except Exception: #No distingue, pero funciona, como puedo distinguir?
		print("El CRD ya existe, pasando al watcher.")

	mi_watcher(cliente) # Activo el watcher de recursos aplicacion.

def mi_watcher(cliente):

    watcher=watch.Watch() # Activo el watcher.

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        print('Estoy en el watcher.')
        objeto = event['object']
        tipo = event['type']

        print("Nuevo evento: ", "Hora del evento: ", datetime.datetime.now(), "Tipo de evento: ", tipo, "Nombre del objeto: ", objeto['metadata']['name'])

        if tipo != 'DELETED':
            # Lógica para llevar el recurso al estado deseado.
            conciliar_spec_status(objeto, cliente)
        if tipo == 'DELETED':
            eliminar_componentes(objeto)
            # Lógica para borrar lo asociado al recurso.

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


	if objeto['spec']['desplegar'] == True:
		listado_componentes_desplegados = cliente.list_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes')
		for i in objeto['spec']['componentes']: # Por cada componente de la aplicacion a desplegar
			permanente = False
			try:
				permanente = i['permanente']
			except KeyError:
				pass
			if (permanente != True):  # Si el componente de la aplicacion esta marcado como permanente y es alguno de los componentes ya desplegados en el cluster y marcado como permanente.
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

def crear_componentes(cliente, componente, app):
	for j in range(app['spec']['replicas']):  # No me convence el aplicar así las replicas
		permanente = False
		try:
			permanente = componente['permanente']
		except KeyError:
			pass
		if permanente == True:
			componente_body = tipos.componente_recurso(componente['name'],
												  componente['image'],
												  componente['previous'],
												  componente['next'], Permanente = True)
			cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente_body)
			break
		else:
			componente_body = tipos.componente_recurso(componente['name'] + '-' + str(j + 1) + '-' + app['metadata']['name'], componente['image'], componente['previous'], componente['next'])
			cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente_body)
		# Creo que es mejor aplicar algún label a los componentes en función de que aplicación formen.
		# Si no distinguimos los nombres bien surge el problema de que los nombres de los componentes al solicitar dos aplicaciones colisionan.

def eliminar_componentes(aplicacion): # Ya no borrará deployments.
	cliente=client.CustomObjectsApi()

	if aplicacion['spec']['desplegar'] == True:
		for i in aplicacion['spec']['componentes']:
			permanente = False
			try:
				permanente = i['permanente']
			except KeyError:
				pass
			if permanente != True:
				for j in range(aplicacion['spec']['replicas']):
					a = i['name'] + '-' + str(j + 1) + '-' +aplicacion['metadata']['name']
					cliente.delete_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', tipos.componente_recurso(i['name'] + '-' + str(j + 1) + '-' +aplicacion['metadata']['name'], i['image'], i['previous'], i['next'])['metadata']['name'])
	elif aplicacion['spec']['desplegar'] == False:
		pass
if __name__ == '__main__':
	controlador()
