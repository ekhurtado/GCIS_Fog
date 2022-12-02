from datetime import datetime
import os,sys

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from pqp import printFile

token = "hkC8oAkLLa43mp6DJQ2maXPWTL1d=A9Caa!?onlkyrtWel3iD9wtF32CWBs4cdEzElxu"
org = "EHU"
bucket = "gcis"

def createBucket():
    print("Creating")
    client = InfluxDBClient(url="http://192.168.1.1:30086", token=token)



def storeData():



    #client = InfluxDBClient(url="http://192.168.233.131:30086", token=token)
    client = InfluxDBClient(url="http://192.168.1.1:30086", token=token)

    printFile("Este es el elemento para la API de Influx")
    service = sys.argv[1]
    if (service == "storeData"):
        machineID = sys.argv[2]
        printFile("Vamos a guardar los datos de la maquina " +str(machineID)+ " en InfluxDB")
        data = sys.argv[3]
        allData = str(data).split("#")
        for d in allData:
            dataType = str(d).split("=")[0]
            dataValue = str(d).split("=")[1]
            printFile(dataType + " - " + dataValue)
            writeMessage = dataType + ",machines="+str(machineID)+" " + dataType + "=" + dataValue

            write_api = client.write_api(write_options=SYNCHRONOUS)
            write_api.write(bucket, org, writeMessage)

            printFile(dataType + " data stored.")
