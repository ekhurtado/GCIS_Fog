# Tipos para la definicion de aplicaciones.
import yaml
import os
import datetime

def CRD_app():
    path = os.path.abspath(os.path.dirname(__file__))
    # rel_path = os.path.join(path, "application_definition.yaml")
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)), "CRD/application_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_aplicacion = yaml.safe_load(stream)
    return CRD_aplicacion

def CRD_comp():
    path = os.path.abspath(os.path.dirname(__file__))
    # rel_path = os.path.join(path, "component_definition.yaml")
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)), "CRD/component_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_componente = yaml.safe_load(stream)
    return CRD_componente

def CRD_app_management_level_i(Nivel_Actual):
    path = os.path.abspath(os.path.dirname(__file__))
    rel_path = os.path.join(os.path.abspath(os.path.join(path, os.pardir)), "CRD/app_management_level_i_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_app_management_level_i = yaml.safe_load(stream)
        CRD_app_management_level_i['metadata']['name']= Nivel_Actual + 's' + '.misrecursos.aplicacion'
        CRD_app_management_level_i['spec']['names']['plural'] = Nivel_Actual + 's'
        CRD_app_management_level_i['spec']['names']['singular'] = Nivel_Actual
        CRD_app_management_level_i['spec']['names']['kind'] = Nivel_Actual.capitalize()
    return CRD_app_management_level_i

def aplicacion(N):
    # N identifica el numero de componentes de la aplicacion.
    aplicacion = {
        'apiVersion': {},
        'kind': 'Aplicacion',
        'metadata':{
            'name': {},
        },
        'spec':{
            'componentes': [0]*N,
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

def componente_recurso(nombre, imagen, anterior, siguiente, **kwargs):
    permanente = kwargs.get('Permanente', None)
    if permanente == None:
        componente_recurso = {
            'apiVersion': 'misrecursos.aplicacion/v1alpha1',
            'kind': 'Componente',
            'metadata':{
                'name': 'componente' + '-' + nombre,
            },
            'spec': {
                'image': imagen,
                'previous': anterior,
                'next': siguiente
            }
        }
    else:
        componente_recurso = {
            'apiVersion': 'misrecursos.aplicacion/v1alpha1',
            'kind': 'Componente',
            'metadata': {
                'name': 'componente' + '-' + nombre,
            },
            'spec': {
                'image': imagen,
                'previous': anterior,
                'next': siguiente,
                'permanente' : permanente
            }
        }
    return componente_recurso

def recurso(objeto, nombre_nivel):
    # N identifica el numero de componentes de la aplicacion.
    if nombre_nivel == 'aplicacion':
        recurso = {
            'apiVersion': 'misrecursos.aplicacion/v1alpha4',
            'kind': nombre_nivel.capitalize(),
            'metadata':{
                'name': objeto['name']
            },
            'spec':
                objeto
        }
    else:
        recurso = {
            'apiVersion': 'misrecursos.aplicacion/v1alpha1',
            'kind': nombre_nivel.capitalize(),
            'metadata': {
                'name': objeto['name']
            },
            'spec':
                objeto
        }
    return recurso

def job_plantilla():
    estructura_job={
        'apiVersion' : 'batch/v1',
        'kind' : 'Job',
        'metadata' : {
          'name' : 'mi-job'
        },
        'spec' : {
            'template' : {
                'spec' : {
                    'containers': [{
                        'name': 'pod-job',
                        'image': 'julencuadra/gcis-fog:pasar-a-ejecucion',
                        'env':[{
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
    job=job_plantilla()
    job['metadata']['name']=job['metadata']['name'] + '-' + nombre
    job['spec']['template']['spec']['containers'][0]['name']= job['spec']['template']['spec']['containers'][0]['name'] + '-' + nombre
    job['spec']['template']['spec']['containers'][0]['env'][0]['value']= nombre
    return job

def evento(mensaje, reason, nombre, nombre_app): # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Event.md
    estructura_evento = {
        'api_Version' : 'v1',
        'event_time' : datetime.datetime.now(),
        'first_timestamp' : datetime.datetime.now(),
        'last_timestamp' :datetime.datetime.now(),
        'action': 'REACCIONO',
        'involvedObject': {
            'apiVersion' : 'misrecursos.aplicacion/v1alpha4',
            'kind' : 'Aplicacion',
            'name' : nombre_app,
            'namespace' : 'default',
            'fieldPath' : 'Events', # No hace nada.
        },
        'kind' : 'Event',
        'message' : mensaje,
        'reason' : reason,
        'type' : 'Normal',
        'metadata':{
            'name' : 'evento-' + nombre
    },
        'reporting_component' : 'Registerer'
    }
    return estructura_evento

def deployment(componente, replicas): # Añadir replicas como input
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
            'labels':{
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
                    },],
                    'nodeSelector': {
                        'node-type': 'multipass'
                    },
                },
            }
        }
    }
    return despliegue

def deploy_app_management_controller(Nivel_Actual, Nivel_Siguiente):

    despliegue = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': Nivel_Actual + '-controller-deployment',
            'labels':{
                'app': Nivel_Actual + '-controller'
            }
        },
        'spec': {
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'app': Nivel_Actual + '-controller'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': Nivel_Actual + '-controller'
                    }
                },
                'spec': {
                    'containers': [{
                        'imagePullPolicy': 'Always',
                        'name': Nivel_Actual + '-controller',
                        'image': 'julencuadra/gcis-fog:generic_app_management_level_controller_image',
                        'ports': [{
                            'containerPort': 80
                        }],
                        'env' : [{
                            'name' : 'LevelName',
                            'value': Nivel_Actual,},{
                            'name' : 'NextLevelName',
                            'value': Nivel_Siguiente,
                        }]
                    },],
                    'nodeSelector': {
                        'node-role.kubernetes.io/master' : 'true'
                    },
                },
            }
        }
    }
    return despliegue

def debug():
    f = open('../CRD/' + 'activo' + '_definition.yaml', 'w')
    yaml.dump(CRD_app_management_level_i('activo', 'aplicacion'), f)

if __name__ == '__main__':
    debug()