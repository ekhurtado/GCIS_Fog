import time
from datetime import datetime

import pytz
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# from kubernetes import client, config

token = "hkC8oAkLLa43mp6DJQ2maXPWTL1d=A9Caa!?onlkyrtWel3iD9wtF32CWBs4cdEzElxu"
org = "EHU"
bucket = "gcis"

# https://github.com/influxdata/influxdb-client-python


def createBucket(name):
    print("Creating bucket")
    # client = InfluxDBClient(url="http://192.168.1.1:30086", token=token)

def getInfluxIP():
    # config.load_incluster_config()
    #
    # cliente_svc = client.CoreV1Api()
    # influx_svc = cliente_svc.read_namespaced_service(name="influxdb-gcis", namespace="default")
    # influx_ip = influx_svc.spec.cluster_ip
    influx_ip = "10.42.1.219"

    print(influx_ip)
    return influx_ip

def storeData(machineID, data):

    #client = InfluxDBClient(url="http://192.168.233.131:30086", token=token)
    influx_ip = getInfluxIP()
    client = InfluxDBClient(url="http://" + influx_ip +":8086", token=token, org=org)

    print("Este es el elemento para la API de Influx")

    print("Vamos a guardar los datos de la maquina " +str(machineID)+ " en InfluxDB")
    allData = str(data).split("#")
    for d in allData:
        dataType = str(d).split("=")[0]
        dataValue = str(d).split("=")[1]
        print(dataType + " - " + dataValue)
        writeMessage = dataType + ",machines="+str(machineID)+" " + dataType + "=" + dataValue

        # data_point = Point(dataType) \
        #     .tag("machines", str(machineID)) \
        #     .tag("location", "Europe/Madrid") \
        #     .field(dataType, float(dataValue))
        data_point = Point(dataType) \
            .tag("machines", str(machineID)) \
            .field(dataType, float(dataValue))

        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket, org, data_point)

        print(dataType + " data stored.")

        tz = pytz.timezone('Europe/Madrid')
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M:%S")
        print("Tiempo actual: " + current_time)



if __name__ == '__main__':
    print("Vamos a publicar datos en influx manualmente")
    disponibilidad = 0.816
    rendimiento = 0.779
    oee = [0.715, 0.760, 0.755, 0.726, 0.690, 0.731, 0.705, 0.682, 0.695, 0.679, 0.640, 0.658, 0.663, 0.681, 0.677, 0.688]
    for current_oee in oee:
        data = "disponibilidad=" + str(disponibilidad) + "#rendimiento=" + str(rendimiento) + "#oee=" + str(current_oee)
        storeData("11", data)
        time.sleep(60)


