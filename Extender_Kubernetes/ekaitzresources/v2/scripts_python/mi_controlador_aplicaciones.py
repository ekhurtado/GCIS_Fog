import os
import sys

import configparser
import urllib3.exceptions
from dateutil import parser
from kubernetes import client, config, watch
import tipos
import datetime

import pytz

# Parámetros de la configuración del objeto
grupo = "misrecursos.aplicacion"
version = "v1alpha4"
namespace = "default"
plural = "aplicaciones"

componentVersion = "v1alpha1"
componentPlural = "componentes"


# TODO si se quieren saber los atributos de un CRD 	> kubectl explain aplicacion --recursive=true


def controlador():
    path = os.path.abspath(os.path.dirname(__file__))
    path = path.replace('Extender_Kubernetes\ekaitzresources', "")
    path = path.replace('\\v2\scripts_python', "")  # Se ha tenido que realizar de este modo ya que con la v daba error
    # path = path.replace("Extender_Kubernetes\ekaitzresources\v2\scripts_python", "")
    config.load_kube_config(os.path.join(os.path.abspath(path), "k3s.yaml"))  # Cargamos la configuracion del cluster

    # TODO Cambiarlo para el cluster
    # TODO PARA AÑADIR LA COMPROBACION DE ESTAR EN EL CLUSTER O FUERA DE EL
    # if 'KUBERNETES_PORT' in os.environ:
    # 	config.load_incluster_config()
    # else:
    # 	config.load_kube_config()

    cliente = client.CustomObjectsApi()  # Creamos el cliente de la API
    cliente_extension = client.ApiextensionsV1Api()  # Creamos el cliente que pueda implementar el CRD.

    try:
        cliente_extension.create_custom_resource_definition(tipos.CRD_app())
        print("Se ha creado la CRD de las aplicaciones. Compruebalo y pulsa una tecla para continuar.")
        input()
    except urllib3.exceptions.MaxRetryError as e:
        print("ERROR DE CONEXION!")
        print("Es posible que la dirección IP del master en el archivo k3s.yaml no sea la correcta")
        controlador()
    except Exception as e:  # No distingue, pero funciona, ¿como puedo distinguir?
        print(str(e))  # Si se quiere mostrar por pantalla el error

        if "Reason: Conflict" in str(e):
            print("El CRD ya existe, pasando al watcher.")
        elif "No such file or directory" in str(e):
            print("No se ha podido encontrar el archivo YAML con la definicion de las aplicaciones. Revisa que todo esta correcto.")
            sys.exit()  # en este caso cierro el programa porque si no se reinicia todo el rato
        # TODO Cuidado al meterlo en un contenedor, no hay que parar el programa ya que se quedaria sin funcionalidad

    mi_watcher(cliente)  # Activo el watcher de recursos aplicacion.


def mi_watcher(cliente):
    watcher = watch.Watch()  # Activo el watcher.
    print('Estoy en el watcher.')
    startedTime = pytz.utc.localize(datetime.datetime.utcnow())  # TODO CUIDADO! En el contenedor habria que instalar pytz

    for event in watcher.stream(cliente.list_namespaced_custom_object, grupo, version, namespace, plural):

        print('He detectado un evento.')
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
                eliminar_componentes(objeto)    # TODO, a parte de eliminar los efimeros tambien hay que actualizar los permanentes que estén en esa aplicacion
                # Lógica para borrar lo asociado al recurso.
            case _:  # default case
                # TODO en nuestro caso es tipo ADDED

                # TODO Creamos el evento notificando que se ha creado la aplicacion
                eventObject = tipos.customResourceEventObject(action='Creado', CR_type="aplicacion",
                                                              CR_object=objeto,
                                                              message='Aplicacion creada correctamente.',
                                                              reason='Created')
                eventAPI = client.CoreV1Api()
                eventAPI.create_namespaced_event("default", eventObject)

                # Lógica para llevar el recurso al estado deseado.
                conciliar_spec_status(objeto, cliente)


def check_modifications(objeto, cliente):
    print("Algo se ha modificado")
    print(objeto)

    # Objeto para la API de los eventos
    eventAPI = client.CoreV1Api()

    # TODO Analizar quien ha realizado el ultimo cambio (el parametro field_manager del metodo patch)
    lastManager = objeto['metadata']['managedFields'][len(objeto['metadata']['managedFields']) - 1]['manager']
    if "componente" in lastManager:
        # Solo si ha actualizado el status un componente realizamos las comprobaciones
        print("Cambio realizado por un componente")

        # Conseguimos el nombre del componente del string del manager
        componentName=lastManager.replace('componente-','')
        componentName=componentName.replace('-' + objeto['metadata']['name'],'')

        # TODO IDEA: El atributo READY es un String ("current/desired")-> comprobar los componentes que estan en running e ir actualizando el current
        #  	Kubernetes no tiene un tipo de datos para hacer el ready 1/3, asi que hay que hacerlo con strings

        # Volvemos a conseguir el objeto de la aplicacion por si se ha modificado
        objeto = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                                        objeto['metadata']['name'])

        runningCount = 0
        for i in range(len(objeto['status']['componentes'])):
            if (objeto['status']['componentes'][i]['status'] == "Running"):  # TODO CUIDADO! Si se añaden replicas habria que comprobar que todas las replicas esten en Running
                runningCount = runningCount + 1

                if (objeto['status']['componentes'][i]['name'] == componentName):
                    # Si el componente que ha enviado el mensaje está a Running, creamos el evento notificándolo
                    eventObject = tipos.customResourceEventObject(action='Creado', CR_type="aplicacion",
                                                                  CR_object=objeto,
                                                                  message= componentName + ' componente desplegado correctamente.',
                                                                  reason='Deploying',)
                    eventAPI.create_namespaced_event("default", eventObject)


        # TODO Otra forma de hacerlo que devuelve los elementos que son Running, luego solo habría que analizar su longitud para saber cuantas hay
        # runningComps = [x for x in objeto['status']['componentes'] if x['status'] == "Running"]

        if runningCount != 0:  # Algún componente está en Running
            objeto['status']['ready'] = str(runningCount) + "/" + objeto['status']['ready'].split("/")[1]

            if runningCount == len(objeto['status']['componentes']):  # Significa que todos los componentes están en running
                objeto['status']['replicas'] = objeto['spec']['replicas']

                # TODO Creamos el evento notificando que se ha creado la aplicacion
                eventObject = tipos.customResourceEventObject(action='Creado', CR_type="aplicacion",
                                                              CR_object=objeto,
                                                              message='Todos los componentes desplegados correctamente.',
                                                              reason='Running')
                eventAPI.create_namespaced_event("default", eventObject)

            # Finalmente, actualizamos el objeto
            field_manager = objeto['metadata']['name']
            cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                          objeto['metadata']['name'], {'status': objeto['status']},
                                                          field_manager=field_manager)

    elif "gestor-ejecuciones" in lastManager:
        print("Se quiere desplegar la aplicacion")
        conciliar_spec_status(objeto, cliente)
    else:
        print("Cambio realizado por una aplicacion")


def conciliar_spec_status(objeto, cliente):
    # Esta funcion es llamada por el watcher cuando hay un evento ADDED o MODIFIED.
    # Habria que chequear las réplicas, las versiones...
    # De momento esta version solo va a mirar el número de réplicas.
    # Chequea si la aplicacion que ha generado el evento está al día en .spec y .status

    cliente_despliegue = client.AppsV1Api()

    # Miro el spec.
    aplicacion_deseada = cliente.get_namespaced_custom_object(grupo, version, namespace, plural,
                                                              objeto['metadata']['name'])

    # Miro el status.
    aplicacion_desplegada = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                        objeto['metadata']['name'])


    # La aplicación crea los componentes que la forman.

    # TODO Creamos el evento de que se indicando que está empezando a crear los componentes

    if objeto['spec']['desplegar'] == True:

        # TODO Creamos el evento notificando que se ha creado la aplicacion
        eventObject = tipos.customResourceEventObject(action='Creado', CR_type="aplicacion",
                                                      CR_object=objeto,
                                                      message='Iniciado despliegue de aplicación.',
                                                      reason='Deploying')
        eventAPI = client.CoreV1Api()
        eventAPI.create_namespaced_event("default", eventObject)

        listado_componentes_desplegados = cliente.list_namespaced_custom_object(grupo, componentVersion, namespace,
                                                                                componentPlural)

        # TODO Primero añadiremos el status en el CR de aplicacion para notificar que sus componentes se están creando.
        #       Para ello, tendremos que analizar cuantos componentes tiene la aplicacion para crear el objeto status

        num_componentes = len(objeto['spec']['componentes'])
        status_object = {'status': {'componentes': [0] * num_componentes, 'replicas': 0,
                                    'ready': "0/" + str(num_componentes)}}  # las réplicas en este punto están a 0
        for i in range(int(num_componentes)):
            status_object['status']['componentes'][i] = {'name': objeto['spec']['componentes'][i]['name'],
                                                         'status': "Creating"}
        cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                      objeto['metadata']['name'], status_object)

        for i in objeto['spec']['componentes']:  # Por cada componente de la aplicacion a desplegar

            permanente = False
            try:
                permanente = i['permanente']
            except KeyError:
                pass
            if (permanente != True):  # Si el componente de la aplicacion no está marcado como permanente se despliega directamente
                crear_componente(cliente, i, objeto)
            else:
                encontrado = False
                for h in listado_componentes_desplegados['items']:  # Por cada componente desplegado en el cluster
                    if (i['name']) == h['metadata']['name']:
                        encontrado = True
                if encontrado:
                    updatePermanent(cliente, i, objeto, action="ADD")    # Si ha encontrado un permanente, se le añadirá la nueva aplicacion a su configuración (configmap)

                    # Se creará el evento notificando que uno de sus componentes ya está desplegado
                    eventObject = tipos.customResourceEventObject(action='Creado', CR_type="aplicacion",
                                                                  CR_object=objeto,
                                                                  message='El componente permanente ' + i['name'] + '  ya estaba desplegado con anterioridad.',
                                                                  reason='Running')
                    eventAPI.create_namespaced_event("default", eventObject)

                    # Volvemos a conseguir la aplicacion para conseguir su status actualizado (puede que otro componente lo haya modificado)
                    appObject = cliente.get_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                                        objeto['metadata']['name'])

                    # También se modificará directamente el status de la aplicacion, para indicar que uno de sus componentes ya está desplegado
                    newRunningCount = int(appObject['status']['ready'].split("/")[0]) + 1
                    appObject['status']['ready'] = str(newRunningCount) + "/" + appObject['status']['ready'].split("/")[1]

                    # Buscamos el componente permanente y lo actualizamos a Running
                    for j in range(len(appObject['status']['componentes'])):
                        if i['name'] == appObject['status']['componentes'][j]['name']:
                            appObject['status']['componentes'][j]['status'] = 'Running'

                        # for i in range(len(objeto['status']['componentes'])):
                        #     if (objeto['status']['componentes'][i]['status'] == "Running"):

                    field_manager = appObject['metadata']['name']
                    cliente.patch_namespaced_custom_object_status(grupo, version, namespace, plural,
                                                                  appObject['metadata']['name'],
                                                                  {'status': appObject['status']},
                                                                  field_manager=field_manager)


                else:
                    crear_componente(cliente, i, objeto)

                    # Si es la primera vez que se despliega el componente permanente tambien se crea y se despliega su ConfigMap
                    crear_permanente_cm(cliente, i, objeto)


    elif objeto['spec']['desplegar'] == False:
        pass

def crear_componente(cliente, componente, app):

    # for j in range(app['spec']['replicas']):  # No me convence el aplicar así las replicas
    permanente = False
    try:
        permanente = componente['permanente']
    except KeyError:
        pass
    if permanente == True:  # En este if se repiten muchos comandos (la linea de crear el objeto, actualizar status...), arreglarlo

        if "customization" in componente:
            componente_body = tipos.componente_recurso(nombre=componente['name'],   # TODO En los permanentes el nombre es único
                                                       nombre_corto=componente['name'],
                                                       imagen=componente['image'],
                                                       anterior=componente['flowConfig']['previous'],
                                                       appName=app['metadata']['name'],
                                                       siguiente=componente['flowConfig']['next'],
                                                       kafkaTopic=componente['kafkaTopic'],
                                                       permanente=True,
                                                       configmap=componente['permanenteCM'],
                                                       customization=componente['customization'])
        else:
            componente_body = tipos.componente_recurso(nombre=componente['name'], # TODO En los permanentes el nombre es único
                                                       nombre_corto=componente['name'],
                                                       imagen=componente['image'],
                                                       anterior=componente['flowConfig']['previous'],
                                                       appName=app['metadata']['name'],
                                                       siguiente=componente['flowConfig']['next'],
                                                       kafkaTopic=componente['kafkaTopic'],
                                                       permanente=True,
                                                       configmap=componente['permanenteCM'])

        cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente_body)

        # break
    else:
        # componente_body = tipos.componente_recurso(
        #     componente['name'] + '-' + str(j + 1) + '-' + app['metadata']['name'], componente['name'],
        #     componente['image'], componente['previous'], componente['next'], componente['kafkaTopic'], componente['customization'], app['metadata']['name'])
        if "customization" in componente:
            componente_body = tipos.componente_recurso(nombre=componente['name'] + '-' + app['metadata']['name'],
            # componente_body = tipos.componente_recurso(nombre=componente['name'] + '-' + str(j + 1) + '-' + app['metadata']['name'],
                                                       nombre_corto=componente['name'],
                                                       imagen=componente['image'],
                                                       anterior=componente['flowConfig']['previous'],
                                                       siguiente=componente['flowConfig']['next'],
                                                       kafkaTopic=componente['kafkaTopic'],
                                                       appName=app['metadata']['name'],
                                                       customization=componente['customization'])
        else:
            componente_body = tipos.componente_recurso(
                nombre=componente['name'] + '-' + app['metadata']['name'],
                # nombre=componente['name'] + '-' + str(j + 1) + '-' + app['metadata']['name'],
                nombre_corto=componente['name'],
                imagen=componente['image'],
                anterior=componente['flowConfig']['previous'],
                siguiente=componente['flowConfig']['next'],
                kafkaTopic=componente['kafkaTopic'],
                appName=app['metadata']['name'])
        cliente.create_namespaced_custom_object(grupo, 'v1alpha1', namespace, 'componentes', componente_body)

    # Creo que es mejor aplicar algún label a los componentes en función de que aplicación formen.
    # Si no distinguimos los nombres bien surge el problema de que los nombres de los componentes al solicitar dos aplicaciones colisionan.

    # TODO Una vez creado el Custom Resource, vamos a añadirle el status de que se están creando los componentes
    status_object = {'status': {'replicas': 0, 'situation': 'Creating'}}
    cliente.patch_namespaced_custom_object_status(grupo, 'v1alpha1', namespace, 'componentes',
                                                  componente_body['metadata']['name'], status_object)

def crear_permanente_cm(cliente, componente, app):

    '''
    Método para crear el configmap asociado al componente permanente
    Este solo se crea la primera vez que aparece el componente permanente
    '''
    print("Creating configmap")

    # Obtenemos la API para gestionar ConfigMaps
    coreAPI = client.CoreV1Api()
    configMapObject = tipos.configmap(componente, app)
    coreAPI.create_namespaced_config_map(namespace=namespace, body=configMapObject)

    # Se creará el evento notificando que el configmap se ha creado
    componentObject = cliente.get_namespaced_custom_object(grupo, componentVersion, namespace, componentPlural,
                                                                                        componente['name'])
    eventObject = tipos.customResourceEventObject(action='Creado', CR_type="componente",
                                                  CR_object=componentObject,
                                                  message='ConfigMap del componente permanente creado. La aplicacion asociada es ' + app['metadata']['name'],
                                                  reason='Created')
    coreAPI.create_namespaced_event("default", eventObject)


def eliminar_componentes(aplicacion):  # Ya no borrará deployments.
    cliente = client.CustomObjectsApi()

    if aplicacion['spec']['desplegar'] == True:
        for i in aplicacion['spec']['componentes']:
            permanente = False
            try:
                permanente = i['permanente']
                if permanente:
                    updatePermanent(cliente, i, aplicacion, action="REMOVE")
            except KeyError:
                pass
            if permanente != True:
                for j in range(aplicacion['spec']['replicas']):
                    cliente.delete_namespaced_custom_object(grupo, componentVersion, namespace, componentPlural,
                                                    i['name'] +'-'+ aplicacion['metadata']['name'])
    elif aplicacion['spec']['desplegar'] == False:
        pass

def eliminar_componente(cliente, componente, aplicacion):  # Ya no borrará deployments.
    # TODO Eliminará un componente de una aplicacion
    print("TODO...")


def updatePermanent(cliente, componente, app, action):
    print("Se va a actualizar el componente permanente ya que ya está desplegado")

    # componentePermanente = cliente.get_namespaced_custom_object_status(grupo, componentVersion, namespace, componentPlural,
    #                                                                     componente['metadata']['name'])

    # Conseguimos el ConfigMap del componente permanente
    configMapName = componente['permanenteCM']
    coreAPI = client.CoreV1Api()
    configMap = coreAPI.read_namespaced_config_map(namespace=namespace, name=configMapName)

    # Conseguimos la información del archivo properties
    cmData = configMap.data
    propertiesFile, propertiesData = list(cmData.items())[0]

    # Parseamos la información para poder trabajar con los datos del archivo properties
    config = configparser.RawConfigParser()
    config.read_string(propertiesData)

    # Variables para los eventps
    eventAPI = client.CoreV1Api()
    eventMessage = ''

    match action:
        case "ADD": # en caso de se haya añadido el elemento permanente a una nueva aplicacion
            # Actualizamos la información de las aplicaciones añadiendo la nueva
            if len(config['InformationSection']) != 0:  # Existe alguna aplicacion
                lastApp = list(config['InformationSection'].keys())[len(config['InformationSection']) - 1]
                newIndex = str(int(lastApp.split(".")[1]) + 1)
            else:   # El componente permanente estaba sin aplicaciones asociadas
                newIndex = '1'
            config.set('InformationSection', 'aplicaciones.' + newIndex, app['metadata']['name'])

            # Actualizamos la información del nuevo topico
            nextComp = tipos.findNextComponent(componente, app)
            config.set('OutTopicSection', app['metadata']['name'] + '.' + nextComp['name'], nextComp['kafkaTopic']) #TODO Pensar como conseguir el topico (de la definicion de la aplicacion conseguir los componentes "next" y sus topicos?)

            # Actualizamos la información del nuevo customization
            for custom in componente['customization']:
                config.set('CustomSection', app['metadata']['name'] + '.' + str.lower(custom.split("=")[0]), custom.split("=")[1])

            # Creamos el mensaje de los eventos
            eventMessage = 'Componente permanente añadido a la aplicacion ' + app['metadata']['name']

        case "REMOVE":  # en caso de se haya eliminado el elemento permanente de una aplicacion
            # TODO CÓDIGO SIN TESTEAR
            if len(config['InformationSection']) == 1: # En este caso es la última aplicación, por lo que hay que eliminar la última aplicacion
                                                            # no se elimina ek componente permanente ni su configmap (queda vacio)
                # Como solo queda una aplicacion, crearemos el string vacio directamente, ya que la informacion anterior no es válida
                stringData = ''
                for section in config.sections():
                    stringData += '[' + section + ']\n' + '\n'  # El segundo salto de linea es para añadir la aplicacion vacia

                # En este caso actualizamos el objeto configmap entero con la API
                configMap.data = {propertiesFile: stringData}
                coreAPI.replace_namespaced_config_map(namespace=namespace, name=configMapName, body=configMap)

                # Creamos el mensaje de los eventos
                eventMessage = 'Componente permanente ya no pertenece a ninguna aplicacion '

                # En este caso, tenemos que enviar el evento porque despues se hace return
                componentObject = cliente.get_namespaced_custom_object(grupo, componentVersion, namespace,
                                                                       componentPlural, componente['name'])
                eventObject = tipos.customResourceEventObject(
                    action='modificado', CR_type="componente",
                    CR_object=componentObject,
                    message=eventMessage,
                    reason='Modified')
                eventAPI.create_namespaced_event("default", eventObject)

                # Salimos del método
                return
            else: # En este caso solo se eliminará la información de la aplicación

                # Eliminamos la aplicacion de la sección de información
                for key in config['InformationSection'].keys():
                    if config['InformationSection'][key] == app['metadata']['name']:
                        print(config['InformationSection'][key])
                        config.remove_option('InformationSection', key)     # TODO Problema con keys con indice ascendente, si eliminas un key intermedio, hay que rehacer los indices?
                                                                                # Al añadir despues cogerá un numero mayor al ultimo, asi que nunca tendria que dar problemas, es algo intuitivo

                # Eliminamos los tópicos
                for key in config['OutTopicSection'].keys():
                    if key.split(".")[0] == app['metadata']['name']:
                        config.remove_option('OutTopicSection', key)

                # Eliminamos los customization
                for key in config['CustomSection'].keys():
                    if key.split(".")[0] == app['metadata']['name']:
                        config.remove_option('CustomSection', key)

                # Creamos el mensaje de los eventos
                eventMessage = 'Componente permanente eliminado de la aplicacion ' + app['metadata']['name']
        case _: # default case
            pass

    # Una vez actualizado los datos del archivo properties, actualizamos el configmap

    # Primero, creamos el string completo
    stringData = ''
    for section in config.sections():
        stringData += '[' + section + ']\n'
        for key in config[section].keys():
            stringData += key + '=' + config[section][key] + '\n'

    # Segundo, actualizamos el objeto configmap con la API
    configMap.data = {propertiesFile: stringData}
    coreAPI.patch_namespaced_config_map(namespace=namespace, name=configMapName, body=configMap)
    print("ConfiMap updated")

    # Se creará el evento notificando a la aplicacion que se ha modificado el componente permanente
    eventObject = tipos.customResourceEventObject(action='modificado', CR_type="aplicacion",
                                                  CR_object=app,
                                                  message='Se ha actualizado el configMap del componente permanente ' +
                                                          componente['name'],
                                                  reason='Modified')
    eventAPI.create_namespaced_event("default", eventObject)

    # También se creará el evento notificando al componente que su configmap se ha modificado
    componentObject = cliente.get_namespaced_custom_object(grupo, componentVersion, namespace, componentPlural,
                                                           componente['name'])
    eventObject = tipos.customResourceEventObject(action='modificado', CR_type="componente",
                                                  CR_object=componentObject,
                                                  message=eventMessage,
                                                  reason='Modified')
    eventAPI.create_namespaced_event("default", eventObject)



if __name__ == '__main__':

    controlador()
