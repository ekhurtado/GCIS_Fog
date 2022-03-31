const fs = require('fs');
const yaml = require('js-yaml');
const os = require('os');

module.exports = function(RED) {
    function PruebaCambioNombre(config) {
        RED.nodes.createNode(this,config);
        this.output = config.output;
        var node = this;
        
        node.on('input', function(msg) {

            //var test =document.querySelectorAll('node-input-output')
            //msg.payload = msg.payload + " " + test

            //node.name = "Nuevo nombre";

            node.label = node.output;

            var aa = RED.util.getObjectProperty(node, "id");

            var bb = node.label;


            msg.payload = " \n ID " + node.id + " \n Label " + bb + " \n ID3 " + aa + " \n Option " + node.output;
            //msg.payload = msg.payload +  " " +node.name+ " recibido por el nodo";

            node.send(msg);
        });
    }

    RED.nodes.registerType("PruebaCambioNombre",PruebaCambioNombre);
}



