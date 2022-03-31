const fs = require('fs');
const yaml = require('js-yaml');

module.exports = function(RED) {
    function CreateFiLApp(config) {
        RED.nodes.createNode(this,config);
        var node = this;
        
        let data = { version: "3.6",
        			services: {}
        			};

		let yamlStr = yaml.safeDump(data);
		fs.writeFileSync('data-out.yml', yamlStr, 'utf8');
		msg.payload = yamlStr;
		node.send(yamlStr);
    }
    RED.nodes.registerType("create-fil-app",CreateFiLApp);
}
