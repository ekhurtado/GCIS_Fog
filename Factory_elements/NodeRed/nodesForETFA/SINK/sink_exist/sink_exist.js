
module.exports = function(RED) {
    function SinkeXist(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;
        
        node.on('input', function(msg) {
            
            /*
            var obj = new Object();
            obj.name = "Raj";
            obj.age  = 32;
            obj.married = false;
            var jsonString= JSON.stringify(obj);
            */

            var inPort = "";
            if (node.function == "storeAssemblyStationData")
                inPort = "TStation";
            else if (node.function == "storeTransportRobotData")
                inPort = "TTransport";
            else if (node.function == "storeMonitorData")
                inPort = "TMonitor";

            const previousName = msg.componentName;


            var previousPayload=JSON.stringify(msg.payload);
            previousPayload = previousPayload.substring(0, previousPayload.length-1);

            myPosition = msg.position + 1;
            
            var message = previousPayload+`,
                "sink-eXist": {
                    "FROM": "gcr.io/clusterekaitz/sink:exist",
                    "ENV1": "FUNCTION=` + node.function +`",
                    "ENV2": "inPort=` + inPort +`",
                    "CMD": "java -jar sink_exist.jar",
                    "POSITION": "` +myPosition+ `"
                }
            }`
            
            // Una vez se tenga todos los Dockerfiles, se enviarán al System Model Component para que los revise
            var responseText = sendDataToSMC(node, JSON.parse(message));

            //node.error(responseText);
            //node.error(JSON.parse(message));
            //node.error(message);
            
            
        });
    }
    RED.nodes.registerType("Sink eXist",SinkeXist);
}



function sendDataToSMC(node, data) {

    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://192.168.233.131:30800/SystemModel/register/", true);

    xhr.onreadystatechange = function () {
        if (this.status == 200) {
            var data = this.responseText;
            if (data == "The application has not been registered.") {
                node.error("!!! " + data);
            }
            console.log(data);
            return data;
        }
    }

    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('seType', 'application');
    xhr.send(JSON.stringify(data));

    //return "Error sending data to System Model Component";
}