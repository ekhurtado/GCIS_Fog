# from kubernetes import client, config
import kafka
import random
import time
from json import dumps

def func_productor():

    print("Started")


    print("Configured")

    f = open("producer.txt", "a")
    f.write("Started\n")
    f.close()

    IP_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns"
    print(IP_server)
    productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='mi-productor', value_serializer=lambda x: dumps(x).encode('utf-8'),
                                    key_serializer=str.encode)
    # productor = kafka.KafkaProducer(bootstrap_servers=[IP_server + ':9092'], client_id='mi-productor')
    #test=productor.bootstrap_connected()
    while True:
        numero = random.randrange(0,10,1)
        print(numero)
        f = open("producer.txt", "a")
        f.write(str(numero) +"\n")
        f.close()
        # productor.send('topico-datos-crudos', value=b'Hola', key=b'App-1') # b'Hola'
        productor.send('topico-datos-crudos', value={'numero': numero, 'key': 'app-1'}, key='App-1') # b'Hola'
        # productor.flush()
        time.sleep(2)

if __name__ == '__main__':
    func_productor()
