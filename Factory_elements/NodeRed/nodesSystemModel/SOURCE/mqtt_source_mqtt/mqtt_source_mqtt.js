
module.exports = function(RED) {
    function MQTTSourceMQTT(config) {
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
                "source-MQTT-MQTT":{
                    "FROM": "gcr.io/clusterekaitz/source:mqtt-mqtt",
                    "ENV1": "FUNCTION=" + node.function,
                    "ENV2": "outPort=" + outPort,
                    "CMD": "python3 source.py"
                }
            }
        };

        node.send(msg);
    }
    RED.nodes.registerType("MQTT - MQTT",MQTTSourceMQTT);
}
