import configparser
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