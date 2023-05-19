const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function CalculosIndicadores(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;
        
        var outPort = "";
        if (node.function == "assemblyStationData")
            outPort = "TDBStation";
        else if (node.function == "transportRobotData")
            outPort = "TDBTransport";
        else if (node.function == "monitorData")
            outPort = "TDBMonitor";

        msg = {
            "payload": {
                "source-MQTT-HTTP":{
                    "FROM": "gcr.io/clusterekaitz/source:exist",
                    "ENV1": "FUNCTION=" + node.function,
                    "ENV2": "outPort=" + outPort,
                    "CMD": "python3 source.py"
                }
            }
        };

        node.send(msg);
    }
    RED.nodes.registerType("Calculos indicadores",CalculosIndicadores);
}
