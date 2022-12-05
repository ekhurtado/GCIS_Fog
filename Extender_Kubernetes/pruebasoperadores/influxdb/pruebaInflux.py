from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from kubernetes import client, config

token = "hkC8oAkLLa43mp6DJQ2maXPWTL1d=A9Caa!?onlkyrtWel3iD9wtF32CWBs4cdEzElxu"
org = "EHU"
bucket = "gcis"


# config.load_incluster_config()
# config.load_kube_config("C:\\Users\\839073\\PycharmProjects\\GCIS_Fog\\k3s.yaml")
config.load_kube_config("/etc/rancher/k3s/k3s.yaml")

cliente_svc = client.CoreV1Api()
influx_svc = cliente_svc.read_namespaced_service(name="influxdb-gcis", namespace="default")
influx_ip = influx_svc.spec.cluster_ip


print(influx_ip)


print("Creating Client")
client = InfluxDBClient(url="http://" + influx_ip +":8086", token=token, org=org)
# client = InfluxDBClient(url="http://10.43.173.216:8086", token=token, org="primary")

print("Client created")

write_api = client.write_api(write_options=SYNCHRONOUS)
write_api.write(bucket, org, "oee,machines=11 oee=0.905")

print("Data stored")