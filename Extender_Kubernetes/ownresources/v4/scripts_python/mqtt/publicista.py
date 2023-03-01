import paho.mqtt.client as mqtt
from json import dumps
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
IP_BROKER = '10.54.13.206'
IP_BROKER = '127.0.0.1'

Plan_de_fabricacion = {
    'flags' : {
        'Control_Flag_New_Service' : 'true',
        'Control_Flag_Item_Completed' : 'false',
        'Control_Flag_Service_Completed' : 'false'
    },
    'str_in' : {
        'Id_Machine_Reference' : '1',
        'Id_Order_Reference' : '1',
        'Id_Batch_Reference' : '1',
        'Id_Ref_Subproduct_Type' : '1',
        'Operation_Ref_Service_Type' : '4',
        'Operation_No_of_Items' : '3'
    }
}

def publicar_plan_fabricacion():

    clienteMqtt = mqtt.Client()
    clienteMqtt.username_pw_set(USER, password=PASSWORD)
    clienteMqtt.connect(IP_BROKER, 31883)
    clienteMqtt.publish('2', payload=dumps(Plan_de_fabricacion).encode('utf-8'))

if __name__ == '__main__':
    publicar_plan_fabricacion()