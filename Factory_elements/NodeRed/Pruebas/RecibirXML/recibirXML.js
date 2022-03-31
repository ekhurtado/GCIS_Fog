const fs = require('fs');
const xml2js = require('xml2js');

module.exports = function(RED) {
    function RecibirXML(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;
        
        node.on('input', function(msg) {

            var inPortName = "";
            if (node.function == "storeAssemblyStationData")
                inPortName = "TStation";
            else if (node.function == "storeTransportRobotData")
                inPortName = "TTransport";
            else if (node.function == "storeMonitorData")
                inPortName = "TMonitor";


            xml2js.parseString(msg, function (err, result) {

                var componentList = result.application.componentInstance;
                var channelList = result.application.channel;

                var newComponent = {
                    $: {
                        name: 'sink_exist_plant_data',
                        type: 'SINK_EXIST',
                        description: 'component instance description'
                    },
                    function: {
                        $: {
                            name: node.function,
                            description: 'description of function'
                        }
                    },
                    inPort: {
                        $: {
                            name: inPortName,
                            id: 'sink_exist_plant_data::' + inPortName
                        },
                        data: {
                            $: {
                                name: 'product',
                                type: 'TPlant'
                            }
                        }
                    }
                };

                channelList[channelList.length-1].$.to='sink_exist_plant_data::' + inPortName;

                componentList.push(newComponent);

                const builder = new xml2js.Builder();
                const xml = builder.buildObject(result);

                var responseText = sendDataToPlanner(node, xml);

                console.log(responseText);
                node.error(responseText);

            });
            
            
        });
    }

    RED.nodes.registerType("RecibirXML",RecibirXML);
}


function sendDataToPlanner(node, data) {

    var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://192.168.233.131:31800/Planner/register/application/", true);

    xhr.onreadystatechange = function () {
        if (this.status == 200) {
            var data = this.responseText;
            /*
            if (data.includes("ERROR")) {
                node.error("!!! " + data);
            }
            */
            //node.error(data);
            console.log(data);
            return data;
        }
    }

    xhr.setRequestHeader('Content-Type', 'application/xml');
    //xhr.setRequestHeader('seType', 'application');
    xhr.send(data);

    //return "Error sending data to System Model Component";
}



