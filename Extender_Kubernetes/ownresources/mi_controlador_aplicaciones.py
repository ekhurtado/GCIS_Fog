from kubernetes import client,config

config.load_kube_config()

cliente=client.CustomObjectsApi()
print("Listado de aplicaciones desplegadas en el cluster.")
cliente.list_cluster_custom_object("misrecursos.aplicacion","v1alpha1","aplicaciones",pretty="true")
aplicacion=cliente.get_namespaced_custom_object("misrecursos.aplicacion","v1alpha1","default","aplicaciones","aplicacion-de-prueba")
#aplicacion=cliente.get_cluster_custom_object("misrecursos.aplicacion","v1alpha1","aplicaciones","aplicacion-de-prueba")

print(aplicacion["metadata"]["name"])
print("	Componentes: " + aplicacion["spec"]["componentes"])
print("	Imagen: " + aplicacion["spec"]["image"])
print("	Nº de replicas: " + str(aplicacion["spec"]["replicas"]))

#print(aplicacion)