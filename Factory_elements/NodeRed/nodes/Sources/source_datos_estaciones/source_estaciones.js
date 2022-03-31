const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function SourceMQTT(config) {
        RED.nodes.createNode(this,config);
        this.machineid = config.machineid;
        this.range = config.range;
        var node = this;
        
        node.on('input', function(msg) {
            //var topic = node.topic;
            //var output = node.output;
            let data = null;
            if (String(node.machineID) == "All") {
                data = { source: {
                        image: "gcr.io/clusterekaitz/appfil2:sde",
                        container_name: "sde",
                        environment: ["RANGE=" + String(node.range), "PQP_NAME=pqp"]
                    }
                };
            } else {
                data = { source: {
                        image: "gcr.io/clusterekaitz/appfil2:sde",
                        container_name: "sde",
                        environment: ["MACHINE_ID="+ String(node.machineid), "RANGE=" + String(node.range), "PQP_NAME=pqp"]
                    }
                };
            }


            let yamlStr = yaml.safeDump(data);
            fs.writeFileSync('def-source-eXist.yml', yamlStr, 'utf8');
            msg.payload = yamlStr;
            node.send(msg);
        });
    }
    RED.nodes.registerType("Datos estaciones",SourceMQTT);
}
