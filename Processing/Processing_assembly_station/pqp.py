import sys,os,json,requests,subprocess
from datetime import datetime, timedelta
from flask import Flask, request
app = Flask(__name__)

# PQP --> Proc Quality Performance

limit = os.environ.get('LIMIT')
function = os.environ.get('FUNCTION')

@app.route('/')
def main():
    return 'Hello! I am the Proc Quality Performance element.\n'


@app.route('/get/tendency/')
def getTendency(dashboardname):


    print("--> Vamos a analizar la tendencia del OEE", file=sys.stderr)

    tend = 'NEG'

    # Falta por hacer

    return 'Tendency of OEE is ' + str(tend) +'\n'


@app.route('/calculate/', methods=['POST'])
def calculate():
    message = ""
    if (function == "processingOEE"):
        message = calculateOEE()

    return message



def calculateOEE():

    print("Limit selected: " + str(limit))
    
    timeRange = request.json['range']
    horaInicio = request.json['start']
    horaFin = request.json['finish']
    machines = request.json['machines']

    if not machines:
        return 'There are no machine IDs'

    for machine in machines:
        machineID = machine['machineID']
        print("--> Vamos a calcular el OEE para la maquina "+str(machineID), file=sys.stderr)

        oee = 0.0
        disponibilidad = 0.0
        rendimiento = 0.0

        actualTimes = machine['actualTimes']
        plannedTimes = machine['plannedTimes']

        #totalTime = float(timeRange) * 60.0;    # Range vendrá en minutos, asi que lo pasaremos a segundos
        totalTime = 60.0;
        totalActualTime = calculateTotalTime(actualTimes, horaInicio, horaFin)
        rendimiento = calculatePerformance(plannedTimes, actualTimes, totalTime, horaFin);

        disponibilidad = totalActualTime / totalTime;
        oee = disponibilidad * rendimiento;

        disponibilidad = round(disponibilidad, 2)
        rendimiento = round(rendimiento, 2)
        oee = round(oee, 2)

        print("-----> Disponibilidad value: " + str(disponibilidad), file=sys.stderr)
        print("-----> Rendimiento value: " + str(rendimiento), file=sys.stderr)
        print("-----> OEE value: " + str(oee), file=sys.stderr)

        print("-----------------------------")
        print("Limit selected: " + str(limit))
    

        oeeLimit = float(limit) / 100
        if (oee < oeeLimit):
            print("OEE below the limit "+limit+": " + str(oee), file=sys.stderr)
            # Primero, crea los nuevos despliegues del cluster
            # De momento le paso el nombre con el .yaml, pero igual seria mejor pasarle solo el nombre y que el manager añada el .yaml
            print("Asking for new event to create new JADE Agent and message printer", file=sys.stderr)
            message = "OEE of machine "+ str(machineID) +" is below the limit ("+limit+"), " + str(oee)
            
            sendCreateDeployMessage("cluster-manager", "message-printer", "False", message)
            sendCreateDeployJADE("cluster-manager", "jade-gateway", "False")


        # Guarda los datos en la BBDD Influx
        calcs = "disponibilidad=" + str(disponibilidad) + "#rendimiento=" + str(rendimiento) + "#oee=" + str(oee)
        subprocess.getoutput('python3 influxAPI.py storeData ' +str(machineID)+ ' ' + str(calcs))
        print("Calcs stored on InfluxDB", file=sys.stderr)

        oee = 0.0
        disponibilidad = 0.0
        rendimiento = 0.0
        totalActualTime = 0.0
        totalTime = 0.0
    
    
    return 'OEE value: ' +str(oee)+ '\n'


def calculateTotalTime(actualTimes, horaInicio, horaFin):
    print("Calculating total time... ", file=sys.stderr)

    totalTime = 0.0
    
    for actual in actualTimes:

        actualStart = actual["Start"]
        actualFinish = actual["Finish"]
        
        if (actualStart < horaInicio):
            actualStart = horaInicio
        if (horaFin < actualFinish):
            actualFinish = horaFin
        resta = calculateDifferenceHours(actualStart, actualFinish)
        totalTime = totalTime + float(resta)

    return totalTime

def calculatePerformance(plannedTimes, actualTimes, totalTime, horaFin):
    print("Calculating performance value... ", file=sys.stderr)

    produccionReal = 0.0
    capacidadProductiva = 0.0
    i = 0

    for actual in actualTimes:
        actualStart = actual["Start"]
        actualFinish = actual["Finish"]
        if (actualFinish < horaFin):
            restaActual = calculateDifferenceHours(actualStart, actualFinish)
            print("##################", file=sys.stderr)
            print("Resta " + str(actualStart) + "-" + str(actualFinish) + "=" + str(restaActual), file=sys.stderr)
            produccionReal = produccionReal + float(restaActual)
            relatedPlannedTime = plannedTimes[i]
            if (relatedPlannedTime["Start"] != None):
                restaPlanned = calculateDifferenceHours(relatedPlannedTime["Start"], relatedPlannedTime["Finish"])
                capacidadProductiva = capacidadProductiva + float(restaPlanned)
        i = i +1
        

    # Una vez tengamos todos los tiempos totales de plan y real, vamos a restar el tiempo total a los dos datos
    if (produccionReal == 0.0):
        produccionReal = 1.0
    if (capacidadProductiva == 0.0):
        capacidadProductiva = 1.0
    produccionReal = totalTime / produccionReal;
    capacidadProductiva = totalTime / capacidadProductiva;
    
    rendimiento = produccionReal / capacidadProductiva;

    return rendimiento


def calculateDifferenceHours(hour1, hour2):
    hora1 = datetime.strptime(hour1, '%H:%M:%S')
    hora2 = datetime.strptime(hour2, '%H:%M:%S')

    resta = hora2 - hora1
    resta  = resta.seconds
    #print("Resta entre " + str(hora1) + " y " + str(hora2) + " en segundos: " + str(resta), file=sys.stderr)

    return resta


def sendCreateDeployMessage(elementName, newDeployName, update, message):
    
    print("Vamos a enviar la peticion de crear el elemento message-printer al EventManager", file=sys.stderr)
    headers = {'Content-Type': 'text/plain'}
    url = 'http://'+elementName+':6000/createDeploy/'+newDeployName+'/'+update+'/'
    r = requests.post(url, headers=headers, data=message)
    print("<-- " + str(r.status_code))

def sendCreateDeployJADE(elementName, newDeployName, update):
    print("Vamos a enviar la peticion de crear un nuevo agente JADE al EventManager", file=sys.stderr)
    headers = {'Content-Type': 'text/plain'}
    url = 'http://'+elementName+':6000/createDeploy/'+newDeployName+'/'+update+'/'
    r = requests.get(url, headers=headers)
    print("<-- " + str(r.status_code))