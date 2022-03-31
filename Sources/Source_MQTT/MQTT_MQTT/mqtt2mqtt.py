import sys, os

def mqtt2mqtt():
    print("Vamos a enviar los datos recogidos al elemento Sink")
    headers = {'Content-Type': 'text/plain'}
    SINK_NAME = os.environ.get('SINK_NAME')

    #url = 'http://'+str(SINK_NAME)+':8080/SinkTomcat/services/updatePLCInfo'
    #r = requests.post(url, headers=headers, data=sys.argv[1])
    #print("<-- " + str(r.status_code))

    print("Sending data with MQTT protocol...")


mqtt2mqtt()