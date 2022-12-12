package functions;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Properties;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import org.xmldb.api.DatabaseManager;
import org.xmldb.api.base.Collection;
import org.xmldb.api.base.CompiledExpression;
import org.xmldb.api.base.Database;
import org.xmldb.api.base.ErrorCodes;
import org.xmldb.api.base.ResourceSet;
import org.xmldb.api.base.XMLDBException;
import org.xmldb.api.modules.XMLResource;
import org.xmldb.api.modules.XQueryService;

import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;

public class StoreAssemblyStationData extends Thread {
	
	// Kafka variables
    private static String Kafka_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns";
    private static String Kafka_topic = "topico-datos-assembly-mqtt";
    
    // eXist variables
    private static Collection dbCollection = null;
    private static String eXistName = "exist";
	
	public void run() {
		System.out.println("GetAssemblyStationData function is running...");
		
		storeAssemblyStationData();
	}
	
	private void storeAssemblyStationData() {
		
		

		// Primero, conseguiremos los datos del topico de Kafka

		String data = null;
		
		printFile("Configurando Consumer...");
		
		Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, Kafka_server + ":9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "Sink-eXist-consumer");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
//        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, org.apache.kafka.connect.json.JsonDeserializer.class.getName());
//	        props.put(ProducerConfig.ACKS_CONFIG, "1");
        
//        KafkaConsumer<String, JsonNode> consumer = new KafkaConsumer<>(props);
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList(Kafka_topic));
        
        printFile("Consumer creado y sucrito a topico");
        
		while (true) {
	        
//            final ConsumerRecords<String, JsonNode> consumerRecords =
//                    consumer.poll(Duration.ofMillis(10000));
            final ConsumerRecords<String, String> consumerRecords =
                    consumer.poll(Duration.ofMillis(10000));
            
            printFile("Comsumer record:");
            printFile(consumerRecords.toString());

            consumerRecords.forEach(record -> {
            	printFile("Mensaje recibido:");
            	printFile(record.toString());
            	
//                System.out.printf("Consumer Record:(%d, %s, %d, %d)\n",
//                        record.key(), record.value(),
//                        record.partition(), record.offset());
                
                processPLCData(record.value());
            });

            consumer.commitAsync();
        }
	        
	        
	        // TODO METER EL WHILE TRUE EN EL MAIN Y QUE CUANDO RECIBA EL MENSAJE SE EJECUTE LA FUNCION
	      
	}
	
	
	
	
	
	private void updatePLCInfo(String plcData) throws XMLDBException {
		
		// Primero, creamos la conexion con eXist-DB
		try {
			connectToExist();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		// Procesar la informacion del PLC
		HashMap<String, String> allPLCInfo = processPLCData(plcData);
		printHashMap(allPLCInfo);
		
		// Conseguir las acciones de la operacion
		ArrayList<String> actionsID = getActionsFromOperation(allPLCInfo.get("Id_Ref_Subproduct_Type"), allPLCInfo.get("Id_Ref_Service_Type"));
		
		// Teniendo todas las acciones vamos a actualizar los datos de la accion del XML del item con los datos del PLC
		for (String action : actionsID) {
			ArrayList<String> attributes = new ArrayList<>();
			// Si el tiempo viene en formato 1970/01/01 00:00:00 hacerlo de esta manera para solo guardar la hora
//					attributes.add("actualStartTime="+ allPLCInfo.get("Data_Initial_Time_Stamp").split(" ")[1]);
//					attributes.add("actualFinishTime="+ allPLCInfo.get("Data_Final_Time_Stamp").split(" ")[1]);
			
			// Si el tiempo viene en timestamp hacerlo de esta manera
			attributes.add("actualStartTime="+ allPLCInfo.get("Data_Initial_Time_Stamp"));
			attributes.add("actualFinishTime="+ allPLCInfo.get("Data_Final_Time_Stamp"));
			
			attributes.add("actualMachineId="+ allPLCInfo.get("Id_Machine_Reference"));
			
			// El itemID hay que construirlo, sumarle el ID que le viene desde la BBDD al id de su batch
			String itemID = allPLCInfo.get("Id_Batch_Reference") + allPLCInfo.get("Id_Item_Number");
			
			updateActionWithXQuery(allPLCInfo.get("Id_Order_Reference"), allPLCInfo.get("Id_Batch_Reference"), itemID, action, attributes);	
		}
				
		System.out.println("Todas las acciones actualizadas");
		
		
	}
	
	private void connectToExist() throws Exception {
		
		try {
            Class existDriver = Class.forName("org.exist.xmldb.DatabaseImpl");
            Database database = (Database) existDriver.newInstance();
            database.setProperty("create-database", "true"); //Creates a new local instance
            DatabaseManager.registerDatabase(database);

            System.out.println(eXistName + " DATABASE DRIVER INITIALIZED");

            String URI = "xmldb:exist://" +eXistName+ ":8080/exist/xmlrpc/db";
            dbCollection = DatabaseManager.getCollection(URI, "admin", "");	// TODO mirar de donde conseguir el usuario y contraseÃ±a

            System.out.println("DATABASE CONNECTION");

            // Sometimes, although the connection to the database is wrong, there is not an exception until
            // a collection is tried to be accessed
            // Therefore, to be sure, an action with the root collection is executed.
            int i = dbCollection.getChildCollectionCount();
            System.out.println("Child collection count --> " + i);	
            System.out.println("DATABASE FIRST QUERY");
            System.out.println("---");

        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        } catch (XMLDBException e2) {
            String message = "Database connection error. ";
            
            switch (e2.errorCode) {
                case ErrorCodes.INVALID_URI:
                    message += "Invalid URI.";
                    break;
                case ErrorCodes.PERMISSION_DENIED:
                    message += "Permission denied.";
                    break;
                case ErrorCodes.VENDOR_ERROR:
                    message += "A vendor specific error has occured (" + e2.vendorErrorCode + "). " + e2.getMessage();
                    message += "\n" + e2.getCause();
                    break;
            }
            throw new Exception (message);
        } catch (Exception e3) {
            e3.printStackTrace();
            throw new Exception ("Database connection error.\n" + e3.toString());
        }
		
	}
	
	private HashMap<String, String> processPLCData(String plcData) {
		// Convert String data in HashMap dictionary
		String[] allDataSplit = plcData.split("&");
        HashMap<String,String> allData = new HashMap<>();
        for (String singleData: allDataSplit)
            allData.put(singleData.split("=")[0], singleData.split("=")[1]);
		return allData;
	}
	
	private void printHashMap(HashMap hashmapObject) {
		Iterator it = hashmapObject.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry pair = (Map.Entry) it.next();
            System.out.println("-> " + pair.getKey() + " = " + pair.getValue());
        }
		System.out.println("---");
	}
	
	private ArrayList<String> getActionsFromOperation(String productID, String operationID) throws XMLDBException {

		System.out.println("Vamos a conseguir las acciones de la operacion "+ operationID + " del producto " + productID);
		// Las definiciones de las operaciones esta en la coleccion generalSkeleton/listOfOperations
    	Collection listOfOperations = dbCollection.getChildCollection("generalSkeleton").getChildCollection("listOfOperations");
    	
    	
    	String[] allOperations = listOfOperations.listResources();
    	ArrayList<String> actions = new ArrayList<>();
		
    	int i = 0;
    	while (i != allOperations.length) {
    		Document xmlFile = (Document) ((XMLResource) listOfOperations.getResource(allOperations[i])).getContentAsDOM();
    		
    		NodeList nList = xmlFile.getElementsByTagName("listOfOperations");
			Node listOfOpNode = nList.item(0);
			Element listOfOpElement = (Element) listOfOpNode;
			
			// Lo vamos a buscar por el ID del producto
			Attr productTypeAttr = listOfOpElement.getAttributeNode("productType");
			if (productTypeAttr.getValue().equals(productID)) {
    			
    			NodeList operationsList = listOfOpElement.getElementsByTagName("operation");
    		    for (int temp = 0; temp < operationsList.getLength(); temp++) {

    		        Node opNode = operationsList.item(temp);
    		        if (opNode.getNodeType() == Node.ELEMENT_NODE) {
    		            Element element = (Element) opNode;
    		            // Sabiendo que es el producto deseado, vamos a buscar la operacion por su ID
    		            if(element.getAttribute("id").equals(operationID)) {
    		            	NodeList actionsList = element.getElementsByTagName("action");
    		            	for (int j = 0; j < actionsList.getLength(); j++) {

    		    		        Node actNode = actionsList.item(j);
    		    		        if (actNode.getNodeType() == Node.ELEMENT_NODE) {
    		    		        	Element actElement = (Element) actNode;
    		    		        	String actionID = actElement.getAttribute("id");
    		    		        	actions.add(actionID);
    		    		        }
    		            	}
    		            	break;
    		    		 }
    		        }
    		    }
    		    break;
    		}
    		i++;
    	}
    	System.out.println("Acciones de la operacion " + operationID + ": " + actions);
    	System.out.println("---");
    	return actions;
	}
	
	// --------------
	// XQUERY METHODS
	// --------------
	private static void updateActionWithXQuery(String orderID, String batchID, String itemID, String actionID, ArrayList<String> attributes) {
		
		String itemFileName = getItemFileByID(orderID, batchID, itemID);

		// Preparamos la sentencia XQuery general (sin los nuevos atributos a insertar)
		String xqueryInsert = "xquery version \"1.0\";\r\n"
				+ "declare namespace i=\"ManufacturingPlan\";\r\n"
				+ "for $a in doc(\"orders/"+orderID+"/"+batchID+"/"+itemFileName+"\")//i:action[@id=\""+actionID+"\"]\r\n"
				+ "return\r\n"
				+ "    update insert attribute ";
		
		for (String attr : attributes) {
			// Añadimos los nuevos atributos y sus valores al xquery
			String xqueryInsertAux = xqueryInsert + attr.split("=")[0] + " {'" + attr.split("=")[1] +"'} into $a";
			
			// Actualizamos el atributo en el XML de la BBDD usando el XQuery
			executeXQuery(xqueryInsertAux);
		}
		
		// Una vez hayamos actualizado todos los atributos, comprobar si el subitem se ha completado
		checkItemOfAction(orderID, batchID, itemFileName, actionID);
	}
	
	
	private static String getItemFileByID(String orderID, String batchID, String itemID) {
		
		try {
			Collection batchCollection = dbCollection.getChildCollection("orders").getChildCollection(orderID).getChildCollection(batchID);
			for (String item : batchCollection.listResources()) {
				Document xmlFile = (Document) ((XMLResource) batchCollection.getResource(item)).getContentAsDOM();
	    		NodeList itemList = xmlFile.getElementsByTagName("item");
    			Node itemNode = itemList.item(0);
    			Element itemElem = (Element) itemNode;
    			// Lo vamos a buscar por el ID del item
    			if (itemElem.getAttribute("item_ID").contentEquals(itemID))
    				return item;
			}
			
		} catch (XMLDBException e) {
			e.printStackTrace();
		}
		return null;
	}
	
	
	private static void executeXQuery(String xquery) {
		
		try {
			ResourceSet res = null;
			XQueryService xqService = (XQueryService) dbCollection.getService("XQueryService", "1.0");
			CompiledExpression compiledQuery = xqService.compile(xquery);
			res = xqService.execute(compiledQuery);
		} catch (XMLDBException e) {
			e.printStackTrace();
		}
	}
	
	private static void checkItemOfAction(String orderID, String batchID, String itemFileName, String actionID) {

		System.out.println("Vamos a comprobar si la accion es la ultima del item (o subitem), es decir, si ya se ha completado ese item");
		try {
			Collection batchCollection = dbCollection.getChildCollection("orders").getChildCollection(orderID).getChildCollection(batchID);
			Document xmlFile = (Document) ((XMLResource) batchCollection.getResource(itemFileName)).getContentAsDOM();
    		NodeList itemList = xmlFile.getElementsByTagName("item");
			Node itemNode = itemList.item(0);
			Element itemElem = (Element) itemNode;
			// Conseguimos todas las acciones del XML
			NodeList allActions = itemElem.getElementsByTagName("action");
			for (int i = 0; i < allActions.getLength(); i++) {
		        Node actionNode = allActions.item(i);
		        if (actionNode.getNodeType() == Node.ELEMENT_NODE) {
		        	Element actionElem = (Element) actionNode;
		        	if (actionElem.getAttribute("id").equals(actionID)) {
		        		// Si he llegado a la accion correcta, conseguir su parent (el subitem) y recorrer todas las acciones mirando si tienen los datos del PLC
		        		Element parentElem = (Element) actionElem.getParentNode();
		        		boolean allCompleted = true;
		        		// Conseguir todas las acciones de ese subitem/item
		        		NodeList actionList = parentElem.getElementsByTagName("action");
		        		for (int j = 0; j < actionList.getLength(); j++) {
		    		        Node parentActionNode = actionList.item(j);
		    		        if (parentActionNode.getNodeType() == Node.ELEMENT_NODE) {
		    		        	Element parentActionElem = (Element) parentActionNode;
		    		        	if (parentActionElem.getAttribute("actualStartTime") == null) {
		    		        		// Si no tiene el atributo actualStartTime quiere decir que hay alguna accion que no se ha completado todavia
		    		        		allCompleted = false;
		    		        		break;
		    		        	}
		    		        }
		        		}
		        		
		        		if (allCompleted) {
		        			// Si estan todas las acciones completadas, hay que cambiar el estado del subitem/item a Completed
		        			String xquery = "xquery version \"1.0\";\r\n"
		        					+ "declare namespace i=\"ManufacturingPlan\";\r\n"
		        					+ "for $a in doc(\"orders/"+orderID+"/"+batchID+"/"+itemFileName+"\")//i:action[@id=\""+actionID+"\"]/..\r\n"
		        					+ "return\r\n"
		        					+ "    update insert attribute state {'Completed'} into $a";
		        			
		        			executeXQuery(xquery);
		        		}
		        		
		        		return;
		        	}
		        }
			}
		} catch (XMLDBException e) {
			e.printStackTrace();
		}
		
		System.out.println("Checked.");
	}
	
	
	// ----------------------------------
	// Metodo por si los datos vienen en formato JSON
	private void processDataJSON(String plcData) {
		System.out.println("Processing data...");
		System.out.println("String:");
		System.out.println(plcData);
		
		JSONParser jsonParser = new JSONParser();
		JSONObject jsonObject = null;
		try {
			jsonObject = (JSONObject) jsonParser.parse(plcData);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		System.out.println("JSON:");
		System.out.println(jsonObject.toString());
		System.out.println(jsonObject.get("start"));
	}
	
	private void printFile(String message) {
		
		try {
			FileWriter fichero = new FileWriter("Sink.txt", true);
			
			fichero.write(message + "\n");
			
			fichero.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        
	}
	

}
