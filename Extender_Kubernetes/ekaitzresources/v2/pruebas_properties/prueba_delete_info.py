import configparser

config = configparser.RawConfigParser()
cc= configparser.ConfigParser


data = '[InformationSection]\naplicaciones.1=data-processing-app-1-model-2\naplicaciones.2=data-processing-app-2-model-2\n[OutTopicSection]\ndata-processing-app-1-model-2.data-processing-1-influx=datos-processing-1-assembly-oee-influx\ndata-processing-app-2-model-2.data-processing-2-influx=datos-processing-2-assembly-oee-influx\n[MachineSection]\ndata-processing-app-1-model-2.limit=72\ndata-processing-app-2-model-2.limit=74'

config.read_string(data)
config.remove_option('InformationSection','aplicaciones.1')
config.remove_option('OutTopicSection','data-processing-app-1-model-2.data-processing-1-influx')
config.remove_option('MachineSection','data-processing-app-1-model-2.limit')

for section in config.sections():
    print("Section: " + section)
    for key in config[section].keys():
        print(" -> " + key + ": " + config[section][key])
    print("--")
print()



# PRUEBAS PARA REMOVE APP



lastActiveApp = list(config['InformationSection'].keys())[0]
print(lastActiveApp)

# config.remove_option('InformationSection',lastActiveApp)
# config.remove_option('')
# config.remove_option('MachineSection', lastActiveApp + '.limit')
# config.remove_section('InformationSection')
# config.add_section('InformationSection')
# config.add_section('InformationSection2')

# print(len(config['InformationSection']))

stringData='hay mas'
if len(config['InformationSection'].keys()) == 1:
    stringData = ''
    for section in config.sections():
        stringData += '[' + section + ']\n' + '\n'  # El segundo salto de linea es para añadir la aplicacion vacia

config2 = configparser.RawConfigParser()
config2.read_string(stringData)
print(len(config2['InformationSection']))


print(data)
print("######################")
print(stringData)
print("######################")

for section in config2.sections():
    print("Section: " + section)
    for key in config2[section].keys():
        print(" -> " + key + ": " + config2[section][key])
    print("--")
print()

config2.set('InformationSection', 'adskhodoaus', 'fsdhbodsj')
print("######################")

for section in config2.sections():
    print("Section: " + section)
    for key in config2[section].keys():
        print(" -> " + key + ": " + config2[section][key])
    print("--")
print()