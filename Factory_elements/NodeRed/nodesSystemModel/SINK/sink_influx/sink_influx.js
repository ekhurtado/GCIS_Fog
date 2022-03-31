
module.exports = function(RED) {
    function SinkInflux(config) {
        RED.nodes.createNode(this,config);
        this.topic = config.topic;
        this.output = config.output;
        var node = this;
        
        node.on('input', function(msg) {

            var inPort = "";
            if (node.function == "storeOEEData")
                inPort = "TStationOEE";
            else if (node.function == "storePerformanceData")
                inPort = "TPerformance";
            else if (node.function == "storeQualityData")
                inPort = "TQuality";
            
            const previousName = msg.componentName;

            var previousPayload=JSON.stringify(msg.payload);
            previousPayload = previousPayload.substring(0, previousPayload.length-1);

            var message = previousPayload+`,
                "sink-influx": {
                    "FROM": "gcr.io/clusterekaitz/sink:influx",
                    "ENV1": "FUNCTION=` + node.function +`",
                    "ENV2": "inPort=` + inPort +`",
                    "CMD": "java -jar sink_influx.jar"
                }
            }`

            node.error(JSON.parse(message));
        });
    }
    RED.nodes.registerType("Influx",SinkInflux);
}
