import tipos
import yaml
import os

# Libreria para pluralizar palabras en diversos idiomas
from inflector import Inflector, English, Spanish

# La imagen Docker de los controladores generales
controller_image = 'ekhurtado/gcis-fog:generic_app_management_level_controller-v4.0'



def generador():
    print('¿Cuantos niveles deseas en tu estructura jerárquica de aplicación?')
    print('Ten en cuenta que hay dos niveles obligatorios, Application y Component.')
    N = int(input())
    App_Management_Level_Number = N - 2
    nombres_niveles = []
    # Primero, conseguimos la informacion de personalizacion del usuario para los niveles genericos
    for j in reversed(range(App_Management_Level_Number)):
        aux=[]
        print('¿Cómo quieres llamar al nivel ' + str(j + 1 +2) +'?')
        levelName = input()
        aux.append(levelName)
        # Ahora, añadimos su plural (suponiendo que ha escrito la palabra en ingles, si no, hay software para detectar idiomas)
        inflector_en = Inflector(English)
        aux.append(inflector_en.pluralize(levelName))
        nombres_niveles.append(aux)

    # Creamos el YAML para el despliegue de cada controlador
    for i in range(App_Management_Level_Number):
        if i < App_Management_Level_Number - 1:
            generador_controlador(nombres_niveles[i], nombres_niveles[i + 1])
        if i == App_Management_Level_Number - 1:
            generador_controlador(nombres_niveles[i], ['application', 'applications'])

    # Generamos los archivos YAML con todos los CRDs
    for i in reversed(range(App_Management_Level_Number)):
        if i == App_Management_Level_Number - 1:
            generador_CRD_tercer_nivel(nombres_niveles[i])
        if i < App_Management_Level_Number - 1:
            generador_CRD_resto_niveles(nombres_niveles[i])

    # Por ultimo, generamos los permisos para cada nivel
    for i in range(App_Management_Level_Number):
        if i < App_Management_Level_Number - 1:
            generador_permisos(nombres_niveles[i], nombres_niveles[i+1])
        if i == App_Management_Level_Number - 1:
            generador_permisos(nombres_niveles[i], ['application', 'applications'])
    # El nivel de componente es diferente, por lo que se creará a parte
    generador_permisos_ultimo_nivel(['component', 'components'])

    os.remove('../CRD/' + 'test_aux.yaml')

def generador_controlador(Nivel_Actual, Nivel_Siguiente):
    f = open('../ficheros_despliegue/' + Nivel_Actual[0] + '_controller_deployment.yaml', 'w')
    yaml.dump(tipos.deploy_app_management_controller(Nivel_Actual, Nivel_Siguiente, controller_image), f)


def generador_CRD_tercer_nivel(Nivel_Actual):

    f = open('../CRD/' + Nivel_Actual[0] + '_definition.yaml', 'w')
    aux = tipos.CRD_app_management_level_i(Nivel_Actual)
    yaml.dump(aux, f)
    file = open('../CRD/' + 'test_aux.yaml', 'w')
    aux_2 = aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']
    aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec'] = {
        'type': 'object',
        'properties': {
            Nivel_Actual[1]: {
                'type': 'array',
                'items': aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']
                ,
            },
            'name': {
                'type': 'string',
            },
            'deploy': {
                'type': 'boolean'
            },
        },
    }

    # En cuanto al status, todos los niveles tendran una lista para conocer el estado de todos sus recursos inferiores
    #   y el parametro "ready" para conocer cuantos de ellos estan en ejecucion
    aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['status'] = tipos.status_object_for_CRDs(Nivel_Actual[1])
    yaml.dump(aux, file)

    f.close()
    file.close()

def generador_CRD_resto_niveles(Nivel_Actual):

    f = open('../CRD/' + Nivel_Actual[0] + '_definition.yaml', 'w')
    with open('../CRD/' + 'test_aux.yaml', 'r') as stream:
        aux = yaml.safe_load(stream)
        aux['metadata']['name'] = Nivel_Actual[1] + '.ehu.gcis.org'
        aux['spec']['names']['plural'] = Nivel_Actual[1]
        aux['spec']['names']['singular'] = Nivel_Actual[0]
        aux['spec']['names']['kind'] = Nivel_Actual[0].capitalize()
    yaml.dump(aux,f)
    aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec'] = {
        'type': 'object',
        'properties': {
            Nivel_Actual[1]: {
                'type': 'array',
                'items': aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']
                ,
            },
            'name': {
                'type': 'string',
            },
            'deploy': {
                'type': 'boolean'
            },
        },
    }

    # En cuanto al status, todos los niveles tendran una lista para conocer el estado de todos sus recursos inferiores
    #   y el parametro "ready" para conocer cuantos de ellos estan en ejecucion
    aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['status'] = tipos.status_object_for_CRDs(Nivel_Actual[1])

    file = open('../CRD/' + 'test_aux.yaml', 'w')
    yaml.dump(aux, file)

def generador_permisos(Nivel_Actual, Nivel_Siguiente):
    f1 = open('../ficheros_despliegue/permisos/' + Nivel_Actual[0] + '_controller_role.yaml', 'w')
    f2 = open('../ficheros_despliegue/permisos/' + Nivel_Actual[0] + '_controller_rolebinding.yaml', 'w')

    yaml.dump(tipos.level_i_role_object(Nivel_Actual[0], Nivel_Actual[1], Nivel_Siguiente[0]), f1)
    yaml.dump(tipos.level_i_role_binding_object(Nivel_Actual[0]), f2)

def generador_permisos_ultimo_nivel(Nivel_Actual):
    # Como el nivel de componente es el ultimo, es diferente a los demas, ya que necesita permisos para gestionar
    #   elementos externos a nuestro modelo, propios de Kubernetes como los Deployments
    f1 = open('../ficheros_despliegue/permisos/' + Nivel_Actual[0] + '_controller_role.yaml', 'w')
    f2 = open('../ficheros_despliegue/permisos/' + Nivel_Actual[0] + '_controller_rolebinding.yaml', 'w')

    yaml.dump(tipos.last_level_role_object(Nivel_Actual[0], Nivel_Actual[1]), f1)
    # En el caso del RoleBinding si es igual al resto de niveles
    yaml.dump(tipos.level_i_role_binding_object(Nivel_Actual[0]), f2)

if __name__ == '__main__':
    generador()
