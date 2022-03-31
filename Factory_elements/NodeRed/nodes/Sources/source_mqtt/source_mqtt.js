const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function SourceMQTT(config) {
        RED.nodes.createNode(this,config);
        this.output = config.output;
        var node = this;
        
        node.on('input', function(msg) {
            //var topic = node.topic;
            //var output = node.output;
            let data = { source: {
                    image: "gcr.io/clusterekaitz/appfil1:source",
                    container_name: "source",
                    environment: ["CLIENT_NAME=sourceMQTT", "TOPIC=#", "SINK_NAME=sink", "OUPUT_GW=" + String(node.output)]
                }
            };


            let yamlStr = yaml.safeDump(data);
            fs.writeFileSync('def-source-mqtt.yml', yamlStr, 'utf8');
            msg.payload = yamlStr;
            node.send(msg);
        });
    }
    RED.nodes.registerType("MQTT",SourceMQTT);
}
