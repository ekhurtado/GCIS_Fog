from random import randint
import time, requests, os
import simplejson as json

cont = 1

def crearNumero():
    numero = randint(1,100)    # Crea un numero aleatorio entre 1 y 100
    print("El numero aleatorio: " + str(numero))
    return numero
    
    
def enviarNumero():
    time.sleep(10)    # Al principio espera 10 segundos
    global cont
    while(cont < 11):    # Repetir hasta 10 veces
        print("Iteracion: " + str(cont))
        randomNum = crearNumero()    # Crear el numero aleatorio
        headers = {'Content-Type': 'application/json'}    # Especificar que el contenido esta en JSON
        params = {'numero': randomNum}    # Contenido del mensaje
        url = 'http://'+ os.environ.get('APPSUMA_HOST') +':'+ os.environ.get('APPSUMA_PORT')
        r = requests.post(url, headers=headers, data=json.dumps(params))    # Enviar HTTP POST
        if(r.status_code != 200):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("CUIDADO!   El mensaje no se ha enviado bien")
        cont = cont + 1
        time.sleep(5) # Esperar 5 segundos
    

print("Comienza la aplicacion crearNumero")
enviarNumero()