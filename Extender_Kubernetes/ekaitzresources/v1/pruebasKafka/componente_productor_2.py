# from kubernetes import client, config
import kafka
import random
import time
from json import dumps

def func_productor():

    IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"
    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='mi-productor-2', value_serializer=lambda x: dumps(x).encode('utf-8'),
                                    key_serializer=str.encode)
    #test=productor.bootstrap_connected()
    while True:
        numero = random.randrange(100,200,1)        
        print(numero)
        # productor.send('topico-datos-crudos', value=numero, key='App-2') # b'Hola'
        productor.send('topico-datos-procesados', value={'numero': numero, 'key': 'app-2'}, key='App-2') # b'Hola'
        # productor.flush()
        time.sleep(2)

if __name__ == '__main__':
    func_productor()