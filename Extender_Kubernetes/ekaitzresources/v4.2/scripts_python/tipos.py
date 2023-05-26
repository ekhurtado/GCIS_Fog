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
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)),
                            "CRD/app_management_level_i_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_app_management_level_i = yaml.safe_load(stream)
        CRD_app_management_level_i['metadata']['name'] = Nivel_Actual[1] + '.ehu.gcis.org'
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


def level_i_role_object(currentLevelName, currentLevelPlural, lowerLevelPlural, higherLevelPlural):
    # TODO, de momento solo se le ha dado permiso para modificar sus componentes y crear los de nivel inferior, ademas
    #       de crear eventos y gestionar CRDs, mas adelante tambien habra que añadir la posibilidad de realizar acciones
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
             'verbs': ["list", "get", "put", "patch", "create", "update", "delete"]
             },
            {'apiGroups': ["ehu.gcis.org"],
             'resources': [higherLevelPlural, higherLevelPlural + "/status"],
             'verbs': ["get", "patch"]
             },
            {'apiGroups': ["apiextensions.k8s.io"],
             'resources': ["customresourcedefinitions"],
             'verbs': ["post", "put", "patch", "create", "update"]
             },
            {'apiGroups': [""],
             'resources': ["events"],
             'verbs': ["watch", "create", "patch", "update", "get"]
             }
        ]
    }

    if currentLevelName == 'application':
        role_object['rules'][-1]['resources'].append('configmaps')  # en el nivel de aplicacion tambien hay que añadir
        # permisos para modificar configmaps, ya que trabaja con componentes permanentes

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
            'name': 'system:serviceaccount:default:service-account-controller-' + currentLevelName,
            'apiGroup': 'rbac.authorization.k8s.io'
        }],
        'roleRef': {
            'kind': 'ClusterRole',
            'name': 'role-controller-' + currentLevelName,
            'apiGroup': 'rbac.authorization.k8s.io'
        }
    }

    return role_binding_object


def level_i_service_account_object(currentLevelName):
    return {
        'apiVersion': 'v1',
        'kind': 'ServiceAccount',
        'metadata': {
            'name': 'service-account-controller-' + currentLevelName,
            'namespace': 'default'  # De momento estamos trabajando en el namespace por defecto
        }
    }


def last_level_role_object(currentLevelName, currentLevelPlural, higherLevelPlural):
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
            {
            'apiGroups': ["ehu.gcis.org"],
            'resources': [higherLevelPlural, higherLevelPlural + "/status"],
            'verbs': ["get", "patch"]
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
             'resources': ["events", "configmaps"],
             'verbs': ["watch", "create", "update", "get"]
             }
        ]
    }

    return role_object


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


def componente_recurso(componenteInfo, appName):
    nombre = componenteInfo['name']
    component_resource = {
        'apiVersion': 'ehu.gcis.org/v1alpha1',
        'kind': 'Component',
        'metadata': {
            'name': nombre,
            'labels': {
                'applicationName': appName,
                'shortName': nombre
            }
        },
        'spec': {
            'name': nombre,
            'image': componenteInfo['image'],
            'flowConfig': componenteInfo['flowConfig']
        }
    }

    # Algunos parametros no son obligatorios, asi que solo los añadiremos si se han definido por el usuario
    if 'customization' in componenteInfo:
        component_resource['spec']['customization'] = componenteInfo['customization']
    if 'permanent' in componenteInfo:
        component_resource['spec']['permanent'] = componenteInfo['permanent']
    elif 'permanent' not in componenteInfo:
        component_resource['spec']['permanent'] = False

    # Hasta aqui tanto el efímero como los permanentes son iguales
    if component_resource['spec']['permanent']:
        # Si 'permanent' es True, creamos su configmap
        component_resource['spec']['permanentCM'] = 'cm-' + nombre
    else:
        # Si no es permanente (es efímero) debemos cambiar su nombre, añadiéndole el de la aplicación
        component_resource['metadata']['name'] = appName + '-' + nombre

    return component_resource


def recurso(grupo, objeto, nombre_nivel, version, parentResourceID, lowerResourceID):
    recurso = {
        'apiVersion': grupo + '/' + version,
        'kind': nombre_nivel.capitalize(),
        'metadata': {
            'name': lowerResourceID,
            'labels': {
                'parentID': parentResourceID
            }
        },
        'spec':
            objeto
    }
    return recurso


def configmap(componente, aplicacion):
    '''
    Method to create the configmap object related to the permanent component
    '''

    # Como se está creando el ConfigMap solo hay una aplicacion
    cmData = '[InformationSection]\n' \
             + 'applications.1=' + aplicacion['metadata']['name'] + '\n' \
             + '[OutTopicSection]\n'

    # En este caso podemos tener mas de un componente posterior
    for allNextComp in componente['flowConfig']['next']:
        cmData += aplicacion['metadata']['name'] + '.' + allNextComp['name'] + '=' + allNextComp['IFMHtopic'] + '\n'

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
                    'serviceAccountName': 'service-account-controller-' + Nivel_Actual[0],
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
                        'env': [{'name': 'KAFKA_KEY',
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

    # TODO modificar: en este caso como solo hemos diseñado aplicaciones sencillas (1 input t 1 output) el topico de
    #  kafka podra ser el mismo y dentro del componente, dependiendo del tipo que sea, lo utilizara para enviar o
    #  recibir. Habria que modificarlo parara que los componentes sean capaces de escuchar por enviar por mas de un
    #  topico y saber diferenciar quien les envia el mensaje o a quien se lo tienen que enviar

    if 'previous' in componente['spec']['flowConfig']:
        # Todos los topicos de entrada serán los mismos, ya que todos los componentes apuntan al topico de entrada del
        # componente, el cual es unico, por eso, solo necesitaremos coger uno de ellos
        deployObject['spec']['template']['spec']['containers'][0]['env'] = \
            deployObject['spec']['template']['spec']['containers'][0]['env'] + [{'name': 'KAFKA_TOPIC',
                                                'value': componente['spec']['flowConfig']['previous'][0]['IFMHtopic']}]

    if 'next' in componente['spec']['flowConfig']:
        # En este caso, habrá que añadir los componentes siguientes con sus topicos asociados. Esto solo se hará en el
        # caso de componentes efimeros ya que en los permanentes está informacion está almacenada en los ConfigMap
        if not componente['spec']['permanent']:
            envVarList = []
            for i in range(len(componente['spec']['flowConfig']['next'])):
                # Por cada siguiente componente añadimos una variable de entorno con toda la informacion (nombre y
                # topico asociado). Despues en el codigo se analizarán todas las variables OUTPUT_IFMH_TOPIC_x
                envVarList.append({'name': 'OUTPUT_IFMH_TOPIC_' + str(i+1), # i+1 ya que comienza en 0
                                   'value': componente['spec']['flowConfig']['next'][i]['name'] +
                                            ';' + componente['spec']['flowConfig']['next'][i]['IFMHtopic']})
            deployObject['spec']['template']['spec']['containers'][0]['env'] = \
                deployObject['spec']['template']['spec']['containers'][0]['env'] + envVarList

    if "customization" in componente['spec']:
        envVarList = []
        for envs in componente['spec']['customization']:
            envVarList.append({'name': envs.split('=')[0],
                               'value': envs.split('=')[1]})
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
        CR_name = CR_name[0:62] + ''.join(random.choices(string.ascii_lowercase + string.digits, k=1))  # tiene que
        # empezar y finalizar con un caracter alfanumerico

    apiVersion = None
    kind = None
    namespace = 'default'  # De momento todos los recursos se despliegan en el default
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
