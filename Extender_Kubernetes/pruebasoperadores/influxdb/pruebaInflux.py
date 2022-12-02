from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


token = "hkC8oAkLLa43mp6DJQ2maXPWTL1d=A9Caa!?onlkyrtWel3iD9wtF32CWBs4cdEzElxu"
org = "EHU"
bucket = "gcis"


print("Creating Client")
client = InfluxDBClient(url="influxdb-gcis:8086", token=token, org="primary")

print("Client created")

org="primary"
bucket = "<BUCKET>"
write_api = client.write_api(write_options=SYNCHRONOUS)
write_api.write(bucket, org, "machines=11")

dbs =  client.get_list_database()

print(dbs)