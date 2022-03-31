const xml2js = require('xml2js');
const fs = require('fs');

module.exports = function(RED) {
    function MQTTSourceHTTP(config) {
        RED.nodes.createNode(this,config);
        this.function = config.function;
        var node = this;

        var outPortName = "";
        if (node.function == "assemblyStationData")
            outPortName = "TStation";
        else if (node.function == "transportRobotData")
            outPortName = "TTransport";
        else if (node.function == "monitorData")
            outPortName = "TMonitor";

        var xmlDef = {
            application: {
                $: {
                    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                    'xsi:noNamespaceSchemaLocation': '/xmlSchemas/Application.xsd',
                    name: 'data_adquisition'
                },
                componentInstance: [
                    {
                        $: {
                            name: 'get_data_from_plant',
                            type: 'MQTT_SOURCE_HTTP',
                            description: 'component instance description'
                        },
                        function: {
                            $: {
                                name: node.function,
                                description: 'description of function'
                            }
                        },
                        outPort: {
                            $: {
                                name: outPortName,
                                id: 'get_data_from_plant::TStation'
                            },
                            data: {
                                $: {
                                    name: 'product',
                                    type: 'TPlant'
                                }
                            }
                        }
                    }
                ],
                channel: [
                    {
                        $: {
                            from: 'get_data_from_plant::TStation',
                            link: 'http'
                        }
                    }
                ]
            }
        };

        const builder = new xml2js.Builder();
        const xml = builder.buildObject(xmlDef);

        node.send(xml);
        
    }
    RED.nodes.registerType("MQTT - HTTP",MQTTSourceHTTP);
}
