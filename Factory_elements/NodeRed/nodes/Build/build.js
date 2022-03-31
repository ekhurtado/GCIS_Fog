const fs = require('fs');
const yaml = require('js-yaml');
const os = require('os');

module.exports = function(RED) {
    function Build(config) {
        RED.nodes.createNode(this,config);
        var node = this;
        
        node.on('input', function(msg) {

            let components = yaml.safeLoad(msg.payload);
            let dockercompose = {version: "3.6",
                    services: components
            };
            
            
            let yamlStr = yaml.safeDump(dockercompose);
            fs.writeFileSync('docker-compose.yml', yamlStr, 'utf8');
            //msg.payload = "<h1>"+yamlStr+"</h1>";
            msg.payload = "<div style=\"font-size: 30px\"><pre lang=\"xml\" >{{"+yamlStr+"}}</pre></div>"
            
            var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
            var xhr = new XMLHttpRequest();
            //xhr.open("POST", "http://192.168.233.131:30800/validate/", true);
            xhr.open("POST", "http://192.168.233.131:30800/SystemModel/register/", true);

            xhr.onreadystatechange = function () {
                if (this.status == 200) {
                    var data = this.responseText;
                    fs.writeFileSync('http-response.txt', data, 'utf8');
                    //msg.payload = "<h1>"+String(data)+"</h1>";
                    msg.payload = data;
                    if (data == "The application has not been registered.") {
                        node.error(data);
                        
                    }

                    console.log(data);
                }
            };

            xhr.setRequestHeader('Content-Type', 'application/x-yaml');
            xhr.send(yaml.dump(dockercompose));

            node.send(msg);
        });
    }
    RED.nodes.registerType("Build",Build);
}



