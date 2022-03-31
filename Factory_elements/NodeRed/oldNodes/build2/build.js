const fs = require('fs');
const yaml = require('js-yaml');


module.exports = function(RED) {
    function Build(config) {
        RED.nodes.createNode(this,config);
        this.name = config.name;
        var node = this;
        
        node.on('input', function(msg) {

            /*
            let fileContents = fs.readFileSync('./data-out.yml', 'utf8');
            let oldDockerCompose = yaml.safeLoad(fileContents);

            let data = { source: {
                        image: "gcr.io/clusterekaitz/appfil1:build",
                        container_name: "build",
                        ports: ["8080:8080"],
                        environment: ["name=" + String(node.name), "SERVICE_TYPE=" + String(node.endpoint)]
                    }
            };

            //let join = Object.assign(oldDockerCompose: { data });

            let yamlStr = yaml.safeDump(data);
            fs.writeFileSync('def-build.yml', yamlStr, 'utf8');
            */
            let components = yaml.safeLoad(msg.payload);
            let dockercompose = {version: "3.6",
                    services: components
            };
            //msg.payload = String(dockercompose)
            
            let yamlStr = yaml.safeDump(dockercompose);
            fs.writeFileSync('docker-compose.yml', yamlStr, 'utf8');
            msg.payload = yamlStr;
            

            node.send(msg);
        });
    }
    RED.nodes.registerType("build2",Build);
}



