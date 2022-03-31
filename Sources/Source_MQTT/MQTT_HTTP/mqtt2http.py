import requests, sys, os

def assemblyStation():
    print("Vamos a enviar los datos recogidos de la estacion de montaje al elemento Sink")
    headers = {'Content-Type': 'text/plain'}
    OUTPUT = os.environ.get('OUTPUT')
    url = 'http://'+str(OUTPUT)+':8080/SinkExist/services/updatePLCInfo'
    
    try:
        r = requests.post(url, headers=headers, data=sys.argv[1])
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:  # This is the correct syntax
        with open('/dataNotSent.txt', 'w') as f:
            f.write(sys.argv[1] + '\n')
        f.close()
        print("CAUTION! The following component is not available, perhaps because it has suffered some failure. The data will be stored until the failure is fixed.")
        return "ERROR: Data not sent."
    
    print("<-- " + str(r.status_code))

def transportRobot():
    print("Vamos a enviar los datos recogidos del robot de transporte al elemento Sink")
    # Los datos se enviaran por HTTP (requests)


function = os.environ.get('FUNCTION')

if (function == "getAssemblyStationData"):
    assemblyStation()
elif (function == "getTransportRobotData"):
    transportRobot()
else:
	print("This function does not exist.")


