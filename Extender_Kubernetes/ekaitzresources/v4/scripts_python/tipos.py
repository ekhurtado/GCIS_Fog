# Tipos para la definicion de aplicaciones.
import random
import string
import pytz
import yaml
import os
import datetime


def CRD_app():
    path = os.path.abspath(os.path.dirname(__file__))
    # rel_path = os.path.join(path, "application_definition.yaml")
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)), "CRD", "application_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_aplicacion = yaml.safe_load(stream)
    return CRD_aplicacion


def CRD_comp():
    path = os.path.abspath(os.path.dirname(__file__))
    # rel_path = os.path.join(path, "component_definition.yaml")
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)), "CRD", "component_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_componente = yaml.safe_load(stream)
    return CRD_componente

def CRD_app_management_level_i(Nivel_Actual):
    path = os.path.abspath(os.path.dirname(__file__))
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)), "CRD/app_management_level_i_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_app_management_level_i = yaml.safe_load(stream)
        CRD_app_management_level_i['metadata']['name']= Nivel_Actual[1] + '.ehu.gcis.org'
        CRD_app_management_level_i['spec']['names']['plural'] = Nivel_Actual[1]
        CRD_app_management_level_i['spec']['names']['singular'] = Nivel_Actual[0]
        CRD_app_management_level_i['spec']['names']['kind'] = Nivel_Actual[0].capitalize()
    return CRD_app_management_level_i


def status_object_for_CRDs(levelPlural):
    return {
        'type': 'object',
        'properties': {
            levelPlural: {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'status': {'type': 'string'}
                    }
                }
            },
            'ready': {'type': 'string'}
        }
    }

def level_i_role_object(currentLevelName, currentLevelPlural, lowerLevelPlural):
    # TODO, de momento solo se le ha dado permiso para modificar sus componentes y crear los de nivel inferior, ademas
    #       de crear eventos y gestionar CRDs, mas adelante tambien habra que añadir la posibilidad de relizar acciones
    #       "patch" en los niveles superiores
    role_object = {
        'apiVersion': 'rbac.authorization.k8s.io/v1',
        'kind': 'ClusterRole',
        'metadata': {
            'name': 'role-controller-' + currentLevelName
        },
        'rules': [{
            'apiGroups': ["ehu.gcis.org"],
            'resources': [currentLevelPlural, currentLevelPlural + "/status"],
            'verbs': ["get", "list", "watch", "patch", "create", "delete"]
            },
            {'apiGroups': ["ehu.gcis.org"],
            'resources': [lowerLevelPlural, lowerLevelPlural + "/status"],
            'verbs': ["post", "put", "patch", "create", "update", "delete"]
             },
            {'apiGroups': ["apiextensions.k8s.io"],
            'resources': ["customresourcedefinitions"],
            'verbs': ["post", "put", "patch", "create", "update"]
             },
            {'apiGroups': [""],
            'resources': ["events"],
            'verbs': ["watch", "create", "update", "get"]
             }
        ]
    }

    return role_object

def level_i_role_binding_object(currentLevelName):

    role_binding_object = {
        'apiVersion': 'rbac.authorization.k8s.io/v1',
        'kind': 'ClusterRoleBinding',
        'metadata': {
            'name': 'role-binding-controller-' + currentLevelName
        },
        'subjects': [{
            'kind': 'User',
            'name': 'system:serviceaccount:default:default',
            'apiGroup': 'rbac.authorization.k8s.io'
        }],
        'roleRef': {
            'kind': 'ClusterRole',
            'name': 'role-controller-' + currentLevelName,
            'apiGroup': 'rbac.authorization.k8s.io'
        }
    }

    return role_binding_object


def last_level_role_object(currentLevelName, currentLevelPlural):
    # Al ser el ultimo nivel, deberá tener permisos para gestionar recursos de su nivel, y, además de poder gestionar
    #   recursos propios de Kubernetes como Deployments
    # TODO, habria que añadir la posibilidad de poder hacer "patch" al status del nivel superior
    role_object = {
        'apiVersion': 'rbac.authorization.k8s.io/v1',
        'kind': 'ClusterRole',
        'metadata': {
            'name': 'role-controller-' + currentLevelName
        },
        'rules': [{
            'apiGroups': ["ehu.gcis.org"],
            'resources': [currentLevelPlural, currentLevelPlural + "/status"],
            'verbs': ["get", "list", "watch", "patch", "create", "delete"]
        },
            {'apiGroups': ["apps"],
             'resources': ["deployments"],
             'verbs': ["post", "put", "patch", "create", "update", "delete"]
             },
            {'apiGroups': ["apps"],
             'resources': ["deployments/status"],
             'verbs': ["get", "list", "watch"]
             },
            {'apiGroups': ["apiextensions.k8s.io"],
             'resources': ["customresourcedefinitions"],
             'verbs': ["post", "put", "patch", "create", "update"]
             },
            {'apiGroups': [""],
             'resources': ["events"],
             'verbs': ["watch", "create", "update", "get"]
             }
        ]
    }

    return role_object


def findNextComponent(currentComponent, app):
    '''
    Method to get the next component given an aplication
    '''
    for comp in app['spec']['components']:
        if comp['name'] == currentComponent['flowConfig']['next']:
            return comp
    return None


def aplicacion(N):
    # N identifica el número de componentes de la aplicacion.
    aplicacion = {
        'apiVersion': {},
        'kind': 'Application',
        'metadata': {
            'name': {},
        },
        'spec': {
            'components': [0] * N,
            'replicas': {}
        }
    }
    return aplicacion


def componente(nombre, imagen, anterior, siguiente, **kwargs):
    componente = {
        'name': nombre,
        'image': imagen,
        'previous': anterior,
        'next': siguiente
    }
    return componente


def componente_recurso(nombre, nombre_corto, imagen, anterior, siguiente, appName, **kwargs):
    component_resource = {
        'apiVersion': 'ehu.gcis.org/v1alpha1',
        'kind': 'Component',
        'metadata': {
            'name': nombre,
            'labels': {
                'applicationName': appName,
                'shortName': nombre_corto
            }
        },
        'spec': {
            'name': nombre_corto,
            'image': imagen,
            'previous': anterior,
            'next': siguiente
            # 'kafkaTopic': kafkaTopic
        }
    }

    #
    if 'all_data' in kwargs:
        if 'customization' in kwargs.get('all_data'):
            component_resource['spec']['customization'] = kwargs.get('all_data')['customization']
        if 'inputIFMHtopic' in kwargs.get('all_data'):
            component_resource['spec']['inputIFMHtopic'] = kwargs.get('all_data')['inputIFMHtopic']
        if 'outputIFMHtopic' in kwargs.get('all_data'):
            component_resource['spec']['outputIFMHtopic'] = kwargs.get('all_data')['outputIFMHtopic']

    # Hasta aqui tanto el efímero como los permanentes son iguales
    if 'permanent' in kwargs:
        component_resource['spec']['permanent'] = kwargs.get('permanent')
        component_resource['spec']['permanentCM'] = kwargs.get('configmap')

    return component_resource


def recurso(grupo, objeto, nombre_nivel, version):

    recurso = {
        'apiVersion': grupo + '/' + version,
        'kind': nombre_nivel.capitalize(),
        'metadata': {
            'name': objeto['name']
        },
        'spec':
            objeto
    }
    return recurso


def configmap(componente, aplicacion):
    '''
    Method to create the configmap object related to the permanent component
    '''

    # Primero
    nextComp = findNextComponent(componente, aplicacion)
    # Como es está creando el ConfigMap solo hay una aplicacion
    cmData = '[InformationSection]\n' \
             + 'applications.1=' + aplicacion['metadata']['name'] + '\n' \
             + '[OutTopicSection]\n' + aplicacion['metadata']['name'] + '.' + nextComp['name'] + '=' + nextComp[
                 'inputIFMHtopic'] + '\n'
                 # 'kafkaTopic'] + '\n'

    cmData += '[CustomSection]\n'
    for custom in componente['customization']:
        cmData += aplicacion['metadata']['name'] + '.' \
                  + str.lower(custom.split("=")[0]) + '=' + custom.split("=")[1] + '\n'

    configMapObject = {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {
            'name': 'cm-' + componente['name']
        },
        'data': {
            componente['name'] + '.properties': cmData
        }
    }

    return configMapObject


def job_plantilla():
    estructura_job = {
        'apiVersion': 'batch/v1',
        'kind': 'Job',
        'metadata': {
            'name': 'mi-job'
        },
        'spec': {
            'template': {
                'spec': {
                    'containers': [{
                        'name': 'pod-job',
                        'image': 'julencuadra/gcis-fog:pasar-a-ejecucion',
                        'env': [{
                            'name': 'NOMBRE_APP',
                            'value': 'Dummy-name'
                        }],
                    }],
                    'restartPolicy': 'OnFailure',
                },
            },
        }
    }
    return estructura_job


def job_pasar_a_ejecucion(nombre):
    job = job_plantilla()
    job['metadata']['name'] = job['metadata']['name'] + '-' + nombre
    job['spec']['template']['spec']['containers'][0]['name'] = job['spec']['template']['spec']['containers'][0][
                                                                   'name'] + '-' + nombre
    job['spec']['template']['spec']['containers'][0]['env'][0]['value'] = nombre
    return job


def evento(mensaje, reason, nombre,
           nombre_app):  # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Event.md
    estructura_evento = {
        'api_Version': 'v1',
        'event_time': datetime.datetime.now(datetime.timezone.utc),
        'first_timestamp': datetime.datetime.now(datetime.timezone.utc),
        'last_timestamp': datetime.datetime.now(datetime.timezone.utc),
        'action': 'REACCIONO',
        'involvedObject': {
            'apiVersion': 'misrecursos.aplicacion/v1alpha4',
            'kind': 'Aplicacion',
            'name': nombre_app,
            'namespace': 'default',
            'fieldPath': 'Events',  # No hace nada.
        },
        'kind': 'Event',
        'message': mensaje,
        'reason': reason,
        'type': 'Normal',
        'metadata': {
            'name': 'evento-' + nombre
        },
        'reporting_component': 'Registerer'
    }
    return estructura_evento


def deployment(componente, replicas):  # Añadir replicas como input
    # with open("/home/julen/Desktop/multipass_k3s/1-create-deployment.yaml", 'r') as stream:
    #     despliegue_de_fichero = yaml.safe_load(stream)
    # despliegue_de_fichero['metadata']['name'] = despliegue_de_fichero['metadata']['name'] + '-' +nombre
    # despliegue_de_fichero['spec']['replicas'] = replicas
    # return despliegue_de_fichero
    despliegue = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': componente['metadata']['name'],
            'labels': {
                'app': 'kafka-test'
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {
                    'app': 'kafka-test'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'kafka-test'
                    }
                },
                'spec': {
                    'containers': [{
                        'imagePullPolicy': 'Always',
                        'name': componente['metadata']['name'],
                        'image': componente['spec']['image'],
                        'ports': [{
                            'containerPort': 80
                        }]
                    }, ],
                    'nodeSelector': {
                        'node-type': 'multipass'
                    },
                },
            }
        }
    }
    return despliegue


def deploy_app_management_controller(Nivel_Actual, Nivel_Inferior, Nivel_Superior, controller_image):

    despliegue = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': Nivel_Actual[0] + '-controller-deployment',
            'labels': {
                'app': Nivel_Actual[0] + '-controller'
            }
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'app': Nivel_Actual[0] + '-controller'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': Nivel_Actual[0] + '-controller'
                    }
                },
                'spec': {
                    'containers': [{
                        'imagePullPolicy': 'Always',
                        'name': Nivel_Actual[0] + '-controller',
                        'image': controller_image,
                        'ports': [{
                            'containerPort': 80
                        }],
                        'env': [{
                            'name': 'LEVEL_NAME',
                            'value': Nivel_Actual[0],
                        }, {
                            'name': 'LEVEL_NAME_PLURAL',
                            'value': Nivel_Actual[1]
                        }, {
                            'name': 'LOWER_LEVEL_NAME',
                            'value': Nivel_Inferior[0],
                        }, {
                            'name': 'LOWER_LEVEL_NAME_PLURAL',
                            'value': Nivel_Inferior[1],
                        }, {
                            'name': 'HIGHER_LEVEL_NAME',
                            'value': Nivel_Superior[0],
                        }, {
                            'name': 'HIGHER_LEVEL_NAME_PLURAL',
                            'value': Nivel_Superior[1],
                        }]
                    }, ],
                    'nodeSelector': {
                        'node-role.kubernetes.io/master': 'true'
                    },
                },
            }
        }
    }
    return despliegue

def deploymentObject(componente, controllerName, appName, replicas, componenteName, **kwargs):
    # TODO Existe la posibilidad de crear el objeto utilizando los objetos de la API
    #       https://github.com/kubernetes-client/python/blob/master/examples/deployment_crud.py

    # nombre del componente solo, sin la aplicacion
    compName = componente['metadata']['name'].replace('-' + appName, '')

    # TODO ELIMINAR, esto es para grabar el video del articulo de Julen,
    #       hay que modificar los componentes para que usen los atributos del articulo
    kafkaTopic = None
    if 'inputIFMHtopic' in componente['spec']:
        kafkaTopic = componente['spec']['inputIFMHtopic']
    elif 'outputIFMHtopic' in componente['spec']:
        kafkaTopic = componente['spec']['outputIFMHtopic']

    deployObject = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': componente['metadata']['name'],
            'labels': {
                'resource.controller': controllerName,
                'component.name': componenteName,
                'applicationName': appName
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {
                    'component.name': componenteName
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'component.name': componenteName
                    }
                },
                'spec': {
                    'containers': [{
                        'imagePullPolicy': 'Always',
                        'name': compName,
                        'image': componente['spec']['image'],
                        'env': [{'name': 'KAFKA_TOPIC',
                                 'value': kafkaTopic},
                                {'name': 'KAFKA_KEY',
                                 'value': appName}]
                    }],
                    'nodeSelector': {
                        'node-type': 'multipass'
                    },
                }
            }
        }
    }

    # Si el nombre de componente sobrepasa los 63 caracteres, lo acortamos
    if len(compName) > 63:
        deployObject['spec']['template']['spec']['containers'][0]['name'] = compName[0:63]

    if "customization" in componente['spec']:
        envVarList = []
        for envs in componente['spec']['customization']:
            envVarList.append({'name': envs.split('=')[0], 'value': envs.split('=')[1]})
        deployObject['spec']['template']['spec']['containers'][0]['env'] = \
            deployObject['spec']['template']['spec']['containers'][0]['env'] + envVarList
        print("TODO: Añadir las variables de entorno necesarias")

    if len(kwargs) != 0:  # en este caso es un componente permanente

        # Conseguimos el configmap y lo añadimos junto a su volumen asociado
        cmName = kwargs.get("configMap")
        volumeMounts = [{'name': componente['metadata']['name'] + '-volume',
                         'mountPath': '/etc/config'}]
        deployObject['spec']['template']['spec']['containers'][0]['volumeMounts'] = volumeMounts
        volumes = [{'name': componente['metadata']['name'] + '-volume',
                    'configMap': {'name': cmName}
                    }]
        deployObject['spec']['template']['spec']['volumes'] = volumes

        # Añadimos el nombre del componente como variable de entorno para que pueda acceder al archivo properties
        newEnv = [{'name': 'COMPONENT_NAME',
                   'value': componenteName}]
        deployObject['spec']['template']['spec']['containers'][0]['env'] = \
            deployObject['spec']['template']['spec']['containers'][0]['env'] + newEnv

    return deployObject


def customResourceEventObject(action, CR_type, CR_object, message, reason):
    create_time = pytz.utc.localize(datetime.datetime.utcnow())

    # Conseguimos la informacion del objeto
    CR_name = CR_object['metadata']['name']
    CR_UID = CR_object['metadata']['uid']
    eventName = CR_object['metadata']['name']

    # Si el nombre de evento va a sobrepasar los 63 caracteres, lo acortamos
    if len(eventName) > (56 - len(action)):  # De los 63 le quitamos los dos '-' y los 5 del random
        eventName = eventName[0:56 - len(action)]

    eventName = eventName + '-' + action + '-' + \
                ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

    # Si el nombre de CR sobrepasa los 63 caracteres, lo acortamos
    if len(CR_name) > 63:
        CR_name = CR_name[0:63]

    apiVersion = None
    kind = None
    namespace = 'default'   # De momento todos los recursos se despliegan en el default
    match CR_type:
        case "application":
            apiVersion = 'ehu.gcis.org/v1alpha4'
            kind = 'Application'
            # namespace = 'default'
        case "component":
            apiVersion = 'ehu.gcis.org/v1alpha1'
            kind = 'Component'
            # namespace = 'default'
        case _:  # en este caso es el nivel generico
            apiVersion = 'ehu.gcis.org/v1alpha1'
            kind = str(CR_type).capitalize()

    return {
        'api_Version': 'v1',
        'eventTime': create_time,
        'firstTimestamp': create_time,
        'lastTimestamp': create_time,
        'action': action,
        'involvedObject': {  # probar tambien con related
            'apiVersion': apiVersion,
            'kind': kind,
            'name': CR_name,
            'namespace': namespace,
            'fieldPath': 'Events',  # No hace nada.
            'uid': CR_UID,
        },
        'kind': 'Event',
        'message': message,
        'reason': reason,
        'reportingComponent': CR_name,
        'reportingInstance': CR_name,
        'type': 'Normal',
        'metadata': {
            'name': eventName,
            'creation_timestamp': create_time
        },
        'source': {
            'component': CR_name
        }
    }
