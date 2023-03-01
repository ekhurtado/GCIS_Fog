import tipos
import yaml
import os

def generador():
    print('¿Cuantos niveles deseas en tu estructura jerárquica de aplicación?')
    print('Ten en cuenta que hay dos niveles obligatorios, Aplicación y Componente.')
    N = int(input())
    App_Management_Level_Number = N - 2
    nombres_niveles = []
    for j in reversed(range(App_Management_Level_Number)):
        aux=[]
        print('¿Cómo quieres llamar al nivel ' + str(j + 1 +2) +'?')
        aux.append(input())
        print('¿Cuál es su plural?')
        aux.append(input())
        nombres_niveles.append(aux)

    for i in range(App_Management_Level_Number):
        if i < App_Management_Level_Number - 1:
            generador_controlador(nombres_niveles[i], nombres_niveles[i + 1])
        if i == App_Management_Level_Number - 1:
            generador_controlador(nombres_niveles[i], ['aplicacion','aplicaciones'])

    for i in reversed(range(App_Management_Level_Number)):
        if i == App_Management_Level_Number - 1:
            generador_CRD_tercer_nivel(nombres_niveles[i])
        if i < App_Management_Level_Number - 1:
            generador_CRD_resto_niveles(nombres_niveles[i])

    os.remove('../CRD/' + 'test_aux.yaml')

def generador_controlador(Nivel_Actual, Nivel_Siguiente):
    f = open('../ficheros_despliegue/' + Nivel_Actual[0] + '_controller_deployment.yaml', 'w')
    yaml.dump(tipos.deploy_app_management_controller(Nivel_Actual, Nivel_Siguiente), f)


def generador_CRD_tercer_nivel(Nivel_Actual):

    f = open('../CRD/' + Nivel_Actual[0] + '_definition.yaml', 'w')
    aux = tipos.CRD_app_management_level_i(Nivel_Actual)
    yaml.dump(aux, f)
    file = open('../CRD/' + 'test_aux.yaml', 'w')
    aux_2 = aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']
    aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec'] = {
        'type': 'object',
        'properties': {
            Nivel_Actual[1]:{
                'type': 'array',
                'items': aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']
                ,
            },
            'name':{
                'type': 'string',
            },
            'desplegar': {
                'type': 'boolean'
            },
        },
    }
    yaml.dump(aux, file)

def generador_CRD_resto_niveles(Nivel_Actual):

    f = open('../CRD/' + Nivel_Actual[0] + '_definition.yaml', 'w')
    with open('../CRD/' + 'test_aux.yaml', 'r') as stream:
        aux = yaml.safe_load(stream)
        aux['metadata']['name'] = Nivel_Actual[1] + '.misrecursos.aplicacion'
        aux['spec']['names']['plural'] = Nivel_Actual[1]
        aux['spec']['names']['singular'] = Nivel_Actual[0]
        aux['spec']['names']['kind'] = Nivel_Actual[0].capitalize()
    yaml.dump(aux,f)
    aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec'] = {
        'type': 'object',
        'properties': {
            Nivel_Actual[1]:{
                'type': 'array',
                'items': aux['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']
                ,
            },
            'name':{
                'type': 'string',
            },
            'desplegar': {
                'type': 'boolean'
            },
        },
    }
    file = open('../CRD/' + 'test_aux.yaml', 'w')
    yaml.dump(aux, file)



if __name__ == '__main__':
    generador()