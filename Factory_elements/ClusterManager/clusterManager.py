from kubernetes import client, config
from os import path
import os,sys,yaml

from flask import Flask, request
app = Flask(__name__)

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config(".kube/config")

from kubernetes import client

# Esto se podria parametrizar, y cada uno que solicita el servicio decidir si quiere actualizarlo o no
update=True

@app.route('/createDeploy/<string:newName>/<string:update>/', methods=['GET','POST'])
def createNewDeploy(newName, update):
    """
    if (newName == "message-printer"):
        messageContent = str(request.data).split("'")[1]
        print("HTTP Content: " + str(messageContent), file=sys.stderr)
        deployMessagePrinter(newName, messageContent)
        return 'Message-printer deploy created.\n'
    """

    if (newName == "jade-gateway"):
        return "Deployed"

    if (isPodOnCluster(newName) == False):
        deploy(newName)
    else:
        if (update == "True"):
            deleteDeploy(newName)
            deploy(newName)
        else:
            print("This deploy is already on cluster.\n", file=sys.stderr)
            return 'Deploy is already on cluster.\n'

    return 'New deploy created.\n'

def isPodOnCluster(newName):

    # BORRAR --> Prueba de external jade
    if (newName == "jade-gateway"):
        newName = "external-jade"
    # De momento lo hara asi, pero estaria bien poder leer el YAML y conseguir el name
    v1 = client.AppsV1Api()
    print("New deploy name " + str(newName), file=sys.stderr)
    deploysList = v1.list_deployment_for_all_namespaces(watch=False)
    for i in deploysList.items:
        if (i.metadata.name == newName):
            print("This deploy is on cluster: " + str(i.metadata.name), file=sys.stderr)
            return True
    return False


def deleteDeploy(newName):
    v1 = client.AppsV1Api()
    print("New deploy name " + str(newName), file=sys.stderr)
    deploysList = v1.list_deployment_for_all_namespaces(watch=False)
    for i in deploysList.items:
        if (i.metadata.name == newName):
            print("Deleting the deploy on cluster..." + str(i.metadata.name), file=sys.stderr)
            v1.delete_namespaced_deployment(newName, i.metadata.namespace)


def deploy(newName):

    with open(path.join(path.dirname(__file__), "/Deployments/" + str(newName) + "-deployment.yaml")) as f:
        dep = yaml.safe_load(f)
        k8s_apps_v1 = client.AppsV1Api()
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=dep, namespace="default")
        print("Deployment created. status='%s'" % resp.metadata.name)


def deployMessagePrinter(newName, messageContent):

    if (isPodOnCluster(newName) == True):   # CAMBIAR AL ID DE LA MAQUINA
        deleteDeploy(newName)

    with open(path.join(path.dirname(__file__), "/Deployments/" + str(newName) + "-deployment.yaml")) as f:
        dep = yaml.safe_load(f)
        #dep['metadata']['name'] = newName  # Si se quiere cambiar el nombre del deployment
        dep['spec']['template']['spec']['containers'][0]['env'][0]['value'] = messageContent
        
        k8s_apps_v1 = client.AppsV1Api()
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=dep, namespace="default")
        print("Message-printer deployment created. status='%s'" % resp.metadata.name)
