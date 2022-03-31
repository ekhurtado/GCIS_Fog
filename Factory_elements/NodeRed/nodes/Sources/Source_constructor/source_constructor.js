const fs = require('fs');
const yaml = require('js-yaml');
const os = require('os');

module.exports = function(RED) {
    function SourceConstructor(config) {
        RED.nodes.createNode(this,config);
        this.sourcetype = config.sourcetype;
        this.output = config.output;
        var node = this;
        
        node.on('input', function(msg) {
            //var topic = node.topic;
            //var output = node.output;
            let data = null;
            if (String(node.sourcetype) == "MQTT") {
                data = { source: {
                        image: "gcr.io/clusterekaitz/appfil1:source",
                        container_name: "source-mqtt",
                        environment: ["CLIENT_NAME=sourceMQTT", "TOPIC=#", "SINK_NAME=sink", "OUPUT_GW=" + String(node.output)]
                    }
                };
            } else if (String(node.sourcetype) == "eXist") {
                data = { source: {
                        image: "gcr.io/clusterekaitz/appfil2:sde",
                        container_name: "sde",
                        environment: ["MACHINE_ID=11", "RANGE=60", "PQP_NAME=pqp"]
                    }
                };
            }

            // https://www.jose-aguilar.com/blog/seleccionar-opcion-para-mostrar-un-formulario-u-otro/
            // https://desarrolloweb.com/articulos/1027.php
            // -> https://desarrolloweb.com/articulos/1281.php

            node.error(data);
            console.log(data);

            let yamlStr = yaml.safeDump(data);
            fs.writeFileSync('def-source-eXist.yml', yamlStr, 'utf8');
            msg.payload = yamlStr;
            node.send(msg);
        });
    }
    RED.nodes.registerType("Source constructor",SourceConstructor);
}



