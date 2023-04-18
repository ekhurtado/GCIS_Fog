import sys, os, json, subprocess
import time
from datetime import datetime
import kafka
from threading import Thread
import configparser

# PQP --> Proc Quality Performance

limit = os.environ.get('LIMIT')
componentName = os.environ.get('COMPONENT_NAME')

IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"  # TODO: Pensar como pasarselo al componente

config = configparser.RawConfigParser()
volumePath = "/etc/config/"


def printFile(message):
    f = open("pqp.txt", "a")
    f.write(str(message) + "\n")
    f.close()


def isPartOfMyApps(desiredAppID):
    config.read(volumePath + componentName + '.properties')
    # Buscamos entre los identificadores de las aplicaciones si está el deseado
    for applicationID in config['InformationSection'].values():
        if applicationID == desiredAppID:
            return True
    return False


def findOutTopics(appID):
    config.read(volumePath + componentName + '.properties')
    # Buscamos los topicos de influx asociados a la aplicación deseada
    allOutTopics = []
    for key in config['OutTopicSection'].keys():
        # Si coincide el ID de la aplicacion, devolvemos el topico de influx situado en el value
        if key.split('.')[0] == appID:
            allOutTopics.append(config['OutTopicSection'][key])
    return allOutTopics


def calculateTotalTime(actualTimes, horaInicio, horaFin):
    print("Calculating total time... ")

    totalTime = 0.0

    for actual in actualTimes:

        actualStart = actual["Start"]
        actualFinish = actual["Finish"]

        if (actualStart < horaInicio):
            actualStart = horaInicio
        if (horaFin < actualFinish):
            actualFinish = horaFin
        resta = calculateDifferenceHours(actualStart, actualFinish)
        printFile(
            "!!!!!! -> La resta de tiempos entre " + str(actualStart) + "-" + str(actualFinish) + ": " + str(resta))
        totalTime = totalTime + float(resta)

    return totalTime


def calculatePerformance(plannedTimes, actualTimes, totalTime, horaFin):
    print("Calculating performance value... ")

    produccionReal = 0.0
    capacidadProductiva = 0.0
    i = 0

    for actual in actualTimes:
        actualStart = actual["Start"]
        actualFinish = actual["Finish"]
        if (actualFinish < horaFin):
            restaActual = calculateDifferenceHours(actualStart, actualFinish)
            print("##################")
            print("Resta " + str(actualStart) + "-" + str(actualFinish) + "=" + str(restaActual))
            produccionReal = produccionReal + float(restaActual)
            relatedPlannedTime = plannedTimes[i]
            if (relatedPlannedTime["Start"] != None):
                restaPlanned = calculateDifferenceHours(relatedPlannedTime["Start"], relatedPlannedTime["Finish"])
                capacidadProductiva = capacidadProductiva + float(restaPlanned)
        i = i + 1

    # Una vez tengamos todos los tiempos totales de plan y real, vamos a restar el tiempo total a los dos datos
    if produccionReal == 0.0:
        produccionReal = 1.0
    if capacidadProductiva == 0.0:
        capacidadProductiva = 1.0
    produccionReal = totalTime / produccionReal
    capacidadProductiva = totalTime / capacidadProductiva

    rendimiento = produccionReal / capacidadProductiva

    return rendimiento


def calculateDifferenceHours(hour1, hour2):
    hora1 = datetime.strptime(hour1, '%H:%M:%S')
    hora2 = datetime.strptime(hour2, '%H:%M:%S')

    resta = hora2 - hora1
    resta = resta.seconds
    # print("Resta entre " + str(hora1) + " y " + str(hora2) + " en segundos: " + str(resta), file=sys.stderr)

    return resta


def sendCreateDeployMessage(elementName, newDeployName, update, message):
    print("Vamos a enviar la peticion de crear el elemento message-printer al EventManager")
    headers = {'Content-Type': 'text/plain'}
    url = 'http://' + elementName + ':6000/createDeploy/' + newDeployName + '/' + update + '/'
    # r = requests.post(url, headers=headers, data=message)
    # print("<-- " + str(r.status_code))


def sendCreateDeployJADE(elementName, newDeployName, update):
    print("Vamos a enviar la peticion de crear un nuevo agente JADE al EventManager")
    headers = {'Content-Type': 'text/plain'}
    url = 'http://' + elementName + ':6000/createDeploy/' + newDeployName + '/' + update + '/'
    # r = requests.get(url, headers=headers)
    # print("<-- " + str(r.status_code))


####################################################
# MÉTODOS DE LOS HILOS DE EJECUCIÓN DE LAS FUNCIONES
####################################################
def performance_function_thread():
    printFile("Hilo de ejecución para la función 'Calculate performance'")

    # TODO BORRAR: PRUEBA PARA LECTURA DE PROPERTIES
    printFile("-> Prueba lectura archivo properties")

    # while True:
    #     config.read(volumePath + 'data-processing-assemblystation.properties')
    #     for section in config.sections():
    #         printFile("--> Section: " + section)
    #         for key in config[section].keys():
    #             printFile(" ----> " + key + ": " + config[section][key])
    #         printFile("----\n")
    #
    #     time.sleep(2)


def oee_function_thread():
    printFile("Hilo de ejecución para la función 'Calculate OEE'")

    # Configuracion Kafka Consumer
    consumidor = kafka.KafkaConsumer(os.environ.get('KAFKA_TOPIC'), bootstrap_servers=[IP_server + ':9092'],
                                     group_id='mi-grupo-transformadores',
                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                                     client_id='mi-consumidor-processing')

    printFile("Limit selected: " + str(limit))

    while True:
        printFile('En el bucle de la función OEE.')

        # Se detectará cuando alguien publique un mensaje en el tópico
        for msg in consumidor:
            printFile('He recibido algo del consumidor.')
            printFile(msg)

            # Conseguimos el identificador de la aplicacion del key del mensaje de Kafka
            # Como está en bytes, lo pasamos a string
            appIDKey = msg.key.decode("utf-8")

            if isPartOfMyApps(appIDKey):
                # Solo vamos a procesar mensajes de aplicaciones en las que está el componente permanente añadido

                msgJSONValue = msg.value

                timeRange = msgJSONValue['range']
                horaInicio = msgJSONValue['start']
                horaFin = msgJSONValue['finish']
                machines = msgJSONValue['machines']

                print(msgJSONValue)
                print(machines)

                if not machines:  # machines is empty
                    print("  ! El mensaje recibido no es correcto. No contiene datos")
                    printFile("  ! El mensaje recibido no es correcto. No contiene datos")
                    continue

                # Como los prints no van bien, guardamos el log en un fichero
                printFile("timeRange:" + str(timeRange) + "\n")
                printFile("horaInicio:" + str(horaInicio) + "\n")
                printFile("horaFin:" + str(horaFin) + "\n")
                printFile("machines:" + str(machines) + "\n\n")

                if not machines:
                    return 'There are no machine IDs'

                for machine in machines:
                    machineID = machine['machineID']
                    printFile("--> Vamos a calcular el OEE para la maquina " + str(machineID))

                    oee = 0.0
                    disponibilidad = 0.0
                    rendimiento = 0.0

                    actualTimes = machine['actualTimes']
                    plannedTimes = machine['plannedTimes']

                    totalTime = float(timeRange) * 60.0  # Range vendrá en minutos, asi que lo pasaremos a segundos
                    # totalTime = 60.0
                    totalActualTime = calculateTotalTime(actualTimes, horaInicio, horaFin)
                    rendimiento = calculatePerformance(plannedTimes, actualTimes, totalTime, horaFin)

                    printFile("Totaltime= " + str(totalTime) + ", actualTime=" + str(totalActualTime))

                    disponibilidad = totalActualTime / totalTime
                    oee = disponibilidad * rendimiento

                    disponibilidad = round(disponibilidad, 3)
                    rendimiento = round(rendimiento, 3)
                    oee = round(oee, 3)

                    printFile("-----> Disponibilidad value: " + str(disponibilidad))
                    printFile("-----> Rendimiento value: " + str(rendimiento))
                    printFile("-----> OEE value: " + str(oee))

                    printFile("-----------------------------")
                    printFile("Limit selected: " + str(limit))

                    oeeLimit = float(limit) / 100
                    if (oee < oeeLimit):
                        printFile("OEE below the limit " + limit + ": " + str(oee))
                        # Primero, crea los nuevos despliegues del cluster
                        # De momento le paso el nombre con el .yaml, pero igual seria mejor pasarle solo el nombre y que el manager añada el .yaml
                        printFile("Asking for new event to create new JADE Agent and message printer")
                        message = "OEE of machine " + str(machineID) + " is below the limit (" + limit + "), " + str(
                            oee)

                        # TODO DE MOMENTO COMENTADO
                        # sendCreateDeployMessage("cluster-manager", "message-printer", "False", message)
                        # sendCreateDeployJADE("cluster-manager", "jade-gateway", "False")

                    # Guarda los datos en la BBDD Influx
                    # Para ello, los enviaremos por Kafka para que Sink Influx los recoja
                    calcs = "disponibilidad=" + str(disponibilidad) + "#rendimiento=" + str(
                        rendimiento) + "#oee=" + str(oee)
                    message = {'machineID': machineID, 'data': calcs}

                    # Configuracion Productor Kafka
                    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'],
                                                    client_id='pqp-assembly-oee',
                                                    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                                                    key_serializer=str.encode)

                    # Busqueda de los topicos por el KEY de la aplicacion recibida (todos los topicos influx asociados
                    # a la ID de la aplicacion)
                    influxTopics = findOutTopics(appIDKey)
                    for topic in influxTopics:
                        # Se envia la informacion a todos los topicos de salida
                        printFile("Se va a enviar la informacion de la app " + appIDKey +
                                  " al topico de influx " + topic)
                        productor.send(topic, value=message, key=appIDKey)

                    # influxAPI.storeData(machineID, calcs)
                    printFile("Calcs stored on InfluxDB")

                    oee = 0.0
                    disponibilidad = 0.0
                    rendimiento = 0.0
                    totalActualTime = 0.0
                    totalTime = 0.0


def trend_function_thread():
    printFile("Hilo de ejecución para la función 'Calculate Trend'")


def main_pqp():
    printFile("Comienzo de ejecución del componente Processing Assembly Station")
    printFile("Started\n")

    # Cada funcion tendrá su hilo de ejecución propio
    thread_func1 = Thread(target=performance_function_thread(), args=())
    thread_func2 = Thread(target=oee_function_thread(), args=())
    thread_func3 = Thread(target=trend_function_thread(), args=())

    thread_func1.start()
    thread_func2.start()
    thread_func3.start()


if __name__ == '__main__':
    main_pqp()
