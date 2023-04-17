import paho.mqtt.client as mqtt
import time, sys, os, subprocess

import mqtt2kafka

MQTT_HOST = "mosquitto"
USER = 'admin'
PASSWORD = 'mosquittoGCIS'
CLIENT_NAME = os.environ.get('MQTT_CLIENT_NAME')
TOPIC = os.environ.get('MQTT_TOPIC')

connected = False

client = mqtt.Client(CLIENT_NAME)
client.username_pw_set(USER, password=PASSWORD)

print("--> Client: " + str(CLIENT_NAME))
print("--> Topic: " + str(TOPIC))

def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


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
    print("Datos del payload: " + str(message.payload))

    if "assembly-station" in message.topic:
        mqtt2kafka.assembly_station_function(message.payload)

    # aux = str(message.payload).split("'")
    # print("Vamos a enviar los datos recogidos al elemento MQTT2HTTP")
    # OUTPUT_GW = os.environ.get('OUTPUT_GW')
    # result = subprocess.getoutput('python3 ' + str(OUTPUT_GW) + ' \"' + str(aux[1]) + "\"")
    # print(result)

    # Intentamos enviar tambien los datos que se han quedado sin enviar
    # dataFile = open('/dataNotSent.txt')
    # for linea in dataFile:
    #   result = subprocess.getoutput('python3 ' +str(OUTPUT_GW)+ ' \"' + str(aux[1]) + "\"")

    sys.stdout.flush()


client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST)
client.loop_start()

while connected != True:    #Wait for connection
    time.sleep(0.1)

client.subscribe(TOPIC, qos=0)

try:
    while True:
        time.sleep(1)

except(KeyboardInterrupt):
    print("exiting")
    client.disconnect()
    client.loop_stop()


# def subscribe(client, clientName, topic, on_message_method):
#     # Method to subscribe to a Mosquitto topic
#
#     print("CLIENT -> " + clientName)
#     print("TOPIC -> " + topic)
#
#     client.on_connect = on_connect
#     client.on_message = on_message
#
#     client.connect(MQTT_HOST)
#     client.loop_start()
#
#     while connected != True:  # Wait for connection
#         time.sleep(0.1)
#
#     client.subscribe(topic, qos=0)
#
#     try:
#         while True:
#             time.sleep(1)
#
#     except(KeyboardInterrupt):
#         print("exiting")
#         client.disconnect()
#         client.loop_stop()
#
#
#
#
