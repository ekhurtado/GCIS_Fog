const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function Source(config) {
        RED.nodes.createNode(this,config);
        this.topic = config.topic;
        this.output = config.output;
        var node = this;
        
        node.on('input', function(msg) {
            //var topic = node.topic;
            //var output = node.output;
            let data = { source: {
                    image: "gcr.io/clusterekaitz/appfil1:source",
                    container_name: "source",
                    environment: ["TOPIC=" + String(node.topic), "OUPUT_GW=" + String(node.output)]
                }
            };


            let yamlStr = yaml.safeDump(data);
            fs.writeFileSync('data-source.yml', yamlStr, 'utf8');
            msg.payload = yamlStr;
            node.send(msg);
        });
    }
    RED.nodes.registerType("source",Source);
}
