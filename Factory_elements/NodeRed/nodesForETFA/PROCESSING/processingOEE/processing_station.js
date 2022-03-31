
module.exports = function(RED) {
    function ProcessingStation(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;
        
        node.on('input', function(msg) {

            var inPort = "";
            var outPort = "";
            if (node.function == "processingOEE") {
                inPort = "TDBStation";
                outPort = "TStationOEE";
            }
            else if (node.function == "processingPerformance") {
                inPort = "TDBPerformance";
                outPort = "TStationPerformance";
            }
            else if (node.function == "processingTrend") {
                inPort = "TDBTrend";
                outPort = "TStationTrend";
            }
            
            const previousName = msg.componentName;

            var previousPayload=JSON.stringify(msg.payload);
            previousPayload = previousPayload.substring(0, previousPayload.length-1);

            myPosition = msg.position + 1;

            var message = `{"payload": 
                    `+previousPayload+`,
                    "processing-station": {
                        "FROM": "gcr.io/clusterekaitz/processing:assembly-station",
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
    RED.nodes.registerType("Assembly station",ProcessingStation);
}
