import configparser
import random
import string

config = configparser.RawConfigParser()
config.read('processing-assembly.properties')
# config.read('data.properties')

print(config.sections())
for section in config.sections():
    print("Section: " + section)
    for key in config[section].keys():
        print(" -> " + key + ": " + config[section][key])
    print("--")
print()
# for key in config['OtraSection'].keys():
#     print(key + ": " + config['OtraSection'][key])
#
# print(config.get('DatabaseSection', 'database.dbname'))

key_received = "data-processing-app-1-model-2"

if key_received in config['InformationSection'].values():
    print("Pertenezco a alguna aplicacion")

for key in config['OutTopicSection'].keys():
    if key_received in key:
        print("El topico de salida para la key que he recibido es: " + config['OutTopicSection'][key] +
              " y pertenece al componente: " + key.split(".")[1])

for key in config['MachineSection'].keys():
    if key_received in key:
        print("El limite de la maquina seleccionada es: " + config['MachineSection'][key])

print("-------------------------------------")
comp = "data-acquisition-1-source-mqtt-kafka-data-acquisition-app-1-model-2"
action = "deesplegando"
print(len(comp))

if len(comp) > (56 - len(action)):
    print("Demasiado largo")
    comp = comp[0:56 - len(action)]
    print(comp)
    print(len(comp))

comp = comp + '-' + action + '-' + \
       ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
print("Resultado")
print(comp)
print(len(comp))
