from datetime import datetime
import os,sys

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = "TYTus1kHWOtBq6Z85LkOM0gdDNeUg_fTMDCsosKXb6XsTwPIlN-2H3Y-bpExFwuvbnmgfkuALD9SMof06MtAwA=="
org = "EHU"
bucket = "gcis"

#client = InfluxDBClient(url="http://192.168.233.131:30086", token=token)
client = InfluxDBClient(url="http://node001:30086", token=token)

print("Este es el elemento para la API de Influx", file=sys.stderr)
service = sys.argv[1]
if (service == "storeData"):
    machineID = sys.argv[2]
    print("Vamos a guardar los datos de la maquina " +str(machineID)+ " en InfluxDB", file=sys.stderr)
    data = sys.argv[3]
    allData = str(data).split("#")
    for d in allData:
        dataType = str(d).split("=")[0]
        dataValue = str(d).split("=")[1]
        print(dataType + " - " + dataValue, file=sys.stderr)
        writeMessage = dataType + ",machines="+str(machineID)+" " + dataType + "=" + dataValue

        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket, org, writeMessage)

        print(dataType + " data stored.", file=sys.stderr)
