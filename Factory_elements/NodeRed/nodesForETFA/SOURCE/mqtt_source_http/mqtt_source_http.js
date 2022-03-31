const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function MQTTSourceHTTP(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;

        var outPort = "";
        if (node.function == "assemblyStationData")
            outPort = "TStation";
        else if (node.function == "transportRobotData")
            outPort = "TTransport";
        else if (node.function == "monitorData")
            outPort = "TMonitor";

        msg = {
            "payload": {
                "source-MQTT-HTTP":{
                    "FROM": "gcr.io/clusterekaitz/source:mqtt-http",
                    "ENV1": "FUNCTION=" + node.function,
                    "ENV2": "outPort=" + outPort,
                    "CMD": "python3 source.py",
                    "POSITION": "1"
                }
            },
            "position": 1
        };

        node.send(msg);
        
    }
    RED.nodes.registerType("MQTT - HTTP",MQTTSourceHTTP);
}
