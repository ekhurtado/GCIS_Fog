const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function ProcessingOEE(config) {
        RED.nodes.createNode(this,config);
        this.limit = config.limit;
        var node = this;
        
        node.on('input', function(msg) {
            //var topic = node.topic;
            //var output = node.output;
            let data = { pqp: {
                    image: "gcr.io/clusterekaitz/appfil2:pqp",
                    container_name: "pqp",
                    ports: ["6000:6000"],
                    environment: ["LIMIT=" + String(node.limit)]
                }
            };


            let yamlStr = yaml.safeDump(data);
            fs.writeFileSync('def-processing-oee.yml', yamlStr, 'utf8');
            msg.payload = yamlStr;
            node.send(msg);
        });
    }
    RED.nodes.registerType("OEE",ProcessingOEE);
}
