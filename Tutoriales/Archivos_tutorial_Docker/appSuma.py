from flask import Flask, request, jsonify
import sys

app = Flask(__name__)
sumaTotal = 0
cont = 0

@app.route('/', methods=['POST', 'GET'])
def index():
    global cont
    global sumaTotal
    if request.method == 'POST':    # Cuando el mensaje HTTP recibido es de tipo POST
        numero = request.json['numero']    # Conseguir el numero del contenido del mensaje HTTP
        print('Numero recibido: ' + str(numero), file=sys.stderr)
        sumaTotal = sumaTotal + numero    # Sumarlo al total
        print('Suma total: ' + str(sumaTotal), file=sys.stderr)
        cont = cont + 1
        if(cont == 10):    # Cuando hemos acabado
            print('################################################################', file=sys.stderr)
            print('Se ha sumado el ultimo numero, este es el resultado:        ' + str(sumaTotal), file=sys.stderr)
            print('################################################################', file=sys.stderr)
        return jsonify("La suma total se ha quedado asi:" + str(sumaTotal))

    if request.method == 'GET':    # Cuando el mensaje HTTP recibido es de tipo POST
        print("La suma hasta ahora: " + str(sumaTotal), file=sys.stderr)
        print("La iteracion en la que estamos: " + str(cont + 1), file=sys.stderr)
        return jsonify("La suma hasta ahora: " + str(sumaTotal))