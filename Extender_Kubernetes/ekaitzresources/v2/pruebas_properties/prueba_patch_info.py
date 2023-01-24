import configparser

config = configparser.RawConfigParser()
cc= configparser.ConfigParser


data = '[InformationSection]\naplicaciones.1=data-processing-app-1-model-2\naplicaciones.2=data-processing-app-2-model-2\n[OutTopicSection]\ndata-processing-app-1-model-2.data-processing-1-influx=datos-processing-1-assembly-oee-influx\ndata-processing-app-2-model-2.data-processing-2-influx=datos-processing-2-assembly-oee-influx\n[MachineSection]\ndata-processing-app-1-model-2.limit=72\ndata-processing-app-2-model-2.limit=74'

config.read_string(data)

for section in config.sections():
    print("Section: " + section)
    for key in config[section].keys():
        print(" -> " + key + ": " + config[section][key])
    print("--")
print()

lastApp = list(config['InformationSection'].keys())[len(config['InformationSection']) - 1]
print(lastApp)
newIndex = str(int(lastApp.split(".")[1]) +1)

# config['InformationSection'][len(config['InformationSection'])] = {'aplicacionbes.3': 'sdifusdfgds'}
config.set('InformationSection', 'aplicaciones.' + newIndex, 'sdifdsufds')

config.set('OutTopicSection', 'sdifdsufds', 'nuevo-topico')

config.set('MachineSection', 'sdifdsufds' + '.limit', '81')

for section in config.sections():
    print("Section: " + section)
    for key in config[section].keys():
        print(" -> " + key + ": " + config[section][key])
    print("--")
print()

stringData = ''
for section in config.sections():
    print("Section: " + section)
    stringData += '[' + section + ']\n'
    for key in config[section].keys():
        stringData += key + ':' + config[section][key] + '\n'
        print(" -> " + key + ": " + config[section][key])
    print("--")
print()

print(data)
print("######################")
print(stringData)

# PRUEBAS PARA REMOVE APP
appToRemove= 'sdifdsufds'

for key in config['InformationSection'].keys():
    if config['InformationSection'][key] == appToRemove:
        print(config['InformationSection'][key])
        config.remove_option('InformationSection', key)

config.remove_option('OutTopicSection', 'sdifdsufds')

config.remove_option('MachineSection', 'sdifdsufds' + '.limit')

for section in config.sections():
    print("Section: " + section)
    stringData += '[' + section + ']\n'
    for key in config[section].keys():
        stringData += key + ':' + config[section][key] + '\n'
        print(" -> " + key + ": " + config[section][key])
    print("--")
print()

print(len(config['InformationSection']))