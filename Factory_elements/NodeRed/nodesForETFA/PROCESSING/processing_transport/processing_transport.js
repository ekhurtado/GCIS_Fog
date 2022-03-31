
module.exports = function(RED) {
    function ProcessingTransport(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;
        
        node.on('input', function(msg) {

            var inPort = "";
            var outPort = "";
            if (node.function == "processingOEE") {
                inPort = "TDBTransport";
                outPort = "TTransportOEE";
            }
            else if (node.function == "processingPerformance") {
                inPort = "TDBPerformance";
                outPort = "TTransportPerformance";
            }
            else if (node.function == "processingTrend") {
                inPort = "TDBTrend";
                outPort = "TTransportTrend";
            }
            
            const previousName = msg.componentName;

            var previousPayload=JSON.stringify(msg.payload);
            previousPayload = previousPayload.substring(0, previousPayload.length-1);

            myPosition = msg.position + 1;

            var message = `{"payload": 
                    `+previousPayload+`,
                    "processing-transport": {
                        "FROM": "gcr.io/clusterekaitz/processing:transport-robot",
                        "ENV1": "FUNCTION=` + node.function +`",
                        "ENV2": "inPort=` + inPort +`",
                        "ENV3": "outPort=` + outPort +`",
                        "CMD": "java -jar processing.jar",
                        "POSITION": "` + myPosition + `"
                    }
                },
                "position": `+myPosition+`
            }`

            //node.error(message);
            node.send(JSON.parse(message));
        });
    }
    RED.nodes.registerType("Transport Robot",ProcessingTransport);
}
