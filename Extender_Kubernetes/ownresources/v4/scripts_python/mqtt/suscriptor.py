import paho.mqtt.client as mqtt
import sys, time
from json import loads
from kubernetes import config, client

MQTT_HOST = "mosquitto"
USER = 'admin'
PASSWORD = 'mosquittoGCIS'

config.load_kube_config("/etc/rancher/k3s/k3s.yaml")
cliente = client.CoreV1Api()
servicios = cliente.list_namespaced_service("default")
j = 0
for i in servicios.items:
    if 'mosquitto' in i.metadata.name:
        break
    j = j + 1
IP_BROKER = servicios.items[j].spec.cluster_ip

def suscriptor():

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            global connected
            connected = True
        else:
            print("Connection failed: ") + str(rc)
        sys.stdout.flush()

    def on_message(client, userdata, message):
        print("Datos del topico: " + str(message.topic))
        aux = str(message.payload).split("'")
        print(message.payload)
        msgDecoded=loads(message.payload.decode('utf-8'))
        print(msgDecoded['flags'])
        print(msgDecoded['str_in'])
        sys.stdout.flush()


    #def on_message(msg):
        #print(msg.payload)

    clienteMqtt = mqtt.Client()
    clienteMqtt.username_pw_set(USER, password=PASSWORD)
    clienteMqtt.connect(IP_BROKER, 1883)
    clienteMqtt.loop_start()
    clienteMqtt.subscribe('2', qos=0)
    clienteMqtt.on_connect = on_connect
    clienteMqtt.on_message = on_message
    while True:
        time.sleep(1)

if __name__ == '__main__':
    suscriptor()