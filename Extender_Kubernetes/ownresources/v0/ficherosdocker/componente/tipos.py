# Tipos para la definicion de aplicaciones.
import yaml
import os

def CRD_app():
    path = os.path.abspath(os.path.dirname(__file__))
    rel_path = os.path.join(path, "application_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_aplicacion = yaml.safe_load(stream)
    return CRD_aplicacion

def CRD_comp():
    path = os.path.abspath(os.path.dirname(__file__))
    rel_path = os.path.join(path, "component_definition.yaml")
    with open(rel_path, 'r') as stream:
        CRD_componente = yaml.safe_load(stream)
    return CRD_componente


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

def componente(nombre, imagen, anterior, siguiente):
    componente = {
        'name': nombre,
        'image': imagen,
        'previous': anterior,
        'next': siguiente
    }
    return componente

def componente_recurso(nombre, imagen, anterior, siguiente):
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
    return componente_recurso

def deployment_aplicacion(nombre, replicas): # Añadir replicas como input
    # with open("/home/julen/Desktop/multipass_k3s/1-create-deployment.yaml", 'r') as stream:
    #     despliegue_de_fichero = yaml.safe_load(stream)
    # despliegue_de_fichero['metadata']['name'] = despliegue_de_fichero['metadata']['name'] + '-' +nombre
    # despliegue_de_fichero['spec']['replicas'] = replicas
    # return despliegue_de_fichero
    despliegue = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'nginx-deployment' + '-' + nombre,
            'labels':{
                'app': 'nginx'
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {
                    'app': 'nginx'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'nginx'
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'nginx',
                        'image': 'piotrzan/nginx-demo:green',
                        'ports': [{
                            'containerPort': 80
                        }],
                        'resources': {
                            'requests': {
                                'cpu': '50m',
                                'memory': '8M'
                            },
                            'limits': {
                                'cpu': '100m',
                                'memory': '16M'
                            }
                        }
                    }],
                    'nodeSelector': {
                        'node-type': 'multipass'
                    },
                },
            }
        }
    }
    return despliegue

def deployment_componente(nombre, replicas): # Añadir replicas como input
    # with open("/home/julen/Desktop/multipass_k3s/1-create-deployment.yaml", 'r') as stream:
    #     despliegue_de_fichero = yaml.safe_load(stream)
    # despliegue_de_fichero['metadata']['name'] = despliegue_de_fichero['metadata']['name'] + '-' +nombre
    # despliegue_de_fichero['spec']['replicas'] = replicas
    # return despliegue_de_fichero
    despliegue = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': 'nginx-deployment' + '-' + nombre,
            'labels':{
                'app': 'nginx'
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {
                    'app': 'nginx'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': 'nginx'
                    }
                },
                'spec': {
                    'containers': [{
                        'name': 'nginx',
                        'image': 'piotrzan/nginx-demo:green',
                        'ports': [{
                            'containerPort': 80
                        }],
                        'resources': {
                            'requests': {
                                'cpu': '50m',
                                'memory': '8M'
                            },
                            'limits': {
                                'cpu': '100m',
                                'memory': '16M'
                            }
                        }
                    }],
                    'nodeSelector': {
                        'node-type': 'multipass'
                    },
                },
            }
        }
    }
    return despliegue
