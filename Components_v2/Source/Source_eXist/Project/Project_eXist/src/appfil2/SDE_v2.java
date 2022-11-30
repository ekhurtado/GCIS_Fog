package appfil2;


import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xmldb.api.DatabaseManager;
import org.xmldb.api.base.Collection;
import org.xmldb.api.base.Database;
import org.xmldb.api.base.ErrorCodes;
import org.xmldb.api.base.XMLDBException;
import org.xmldb.api.modules.XMLResource;

import com.google.gson.JsonObject;


public class SDE_v2 {
	
	// SDE --> Source Datos Estaciones
	
	// eXist variables
    private static String serverExist = "http://exist:8080";
    private static String eXistName = "exist";
    private static Collection dbCollection = null;  // Root collection of the repository
    
    // Kafka variables
    public static String Kafka_server = "mi-cluster-mensajeria-kafka-bootstrap.kafka-ns";

    //Error Messages
    private static final String PERMISSION_DENIED_EXCEPTION = "org.exist.security.PermissionDeniedException";
    private static final String PERMISSION_DENIED_EXCEPTION_MESSAGE = "Permission denied";

    private static AllInfo machineInfo = null;
    
	public static void main(String[] args) {
	
		String function = System.getenv("FUNCTION");
		
		if (function.equals("getAssemblyStationData"))
			getAssemblyStationData();
	}
	
	

	private static void getAssemblyStationData() {
		
		
		// Ahora, cada 15 minutos, analizara la base de datos, y guardara el calculo del analisis
		while(true) {
			
			try {
				Thread.sleep(60000);	// 1 minuto
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			// Primero se va a conectar a la BBDD eXist
			try {
				connectToeXist();
			} catch (Exception e) {
				e.printStackTrace();
			}
			
			// Cogemos las variables de entorno con las que se modela la aplicacion
			String machineID = System.getenv("MACHINE_ID");
			String output = System.getenv("OUTPUT");
			int rangeMinute = Integer.parseInt(System.getenv("RANGE"));
			int range = rangeMinute * 60000;	// Como el range nos los van a pasar en minutos, hay que pasarlo a milisegundos

			Date date = new Date();
			DateFormat hourFormat = new SimpleDateFormat("HH:mm:ss");
			hourFormat.setTimeZone(TimeZone.getTimeZone("Europe/Madrid"));
			String horaFin = hourFormat.format(date);

			date.setTime(date.getTime()- range);
			String horaInicio = hourFormat.format(date);
			
			DateFormat dateFormat = new SimpleDateFormat("YYYY/MM/dd");
			hourFormat.setTimeZone(TimeZone.getTimeZone("Europe/Madrid"));
			String fecha = dateFormat.format(date);
			
			boolean machineWorking = false;
			
			// TODO: Borrar ES PARA PRUEBAS!!!
//			horaInicio = "11:15:00";
//			horaFin = "12:15:00";
			
			System.out.println("MACHINEID = " + machineID);
			
			System.out.println("-----------------> Fecha: " + fecha);
			System.out.println("-----------------> Intervalo de tiempo: "+horaInicio+" - " + horaFin);

			// Recorrera toda la BBDD guardando todos los datos de la maquina deseada
			try {
				JSONObject json = new JSONObject();
				JSONArray machinesArray = new JSONArray();
				
				if (!machineID.equals("NULL")) {
					
					getMachineInfo(machineID, horaInicio, horaFin);
					
					if (machineInfo == null) {
						System.out.println("La base de datos no tiene la estructura correcta.");
					
						continue;
					} else if ((machineInfo.getActualTimes().isEmpty())) {
						System.out.println("Esta maquina no ha trabajado en este intervalo de tiempo.");
						
						continue;
					} else {
						System.out.println("Operaciones realizadas por la maquina "+machineID+" en el intervalo de tiempo establecido:");
						System.out.println("-------------");
						System.out.println("MachineID: " + machineInfo.getMachineID());
						System.out.println("ActualTimes: " + machineInfo.actualTimesToString());
						System.out.println("PlannedTimes: " + machineInfo.plannedTimesToString());
						System.out.println("-------------");
						
	
			            // Vamos a crear el JSON con toda la informacion de la maquina
			            JSONObject jsonAux = machineInfo.getJSON();
			            machinesArray.add(jsonAux);
			            json.put("machines", machinesArray);
			            
			            machineWorking = true;
					}
				} else {
					// Si no hemos especificado ninguna maquina, machineID tendrá el valor de "NULL"
					// En este caso, analizaremos toda la base de datos
					
					ArrayList<AllInfo> allMachineInfo = getAllMachineInfo(horaInicio, horaFin, fecha);
					if (allMachineInfo == null) {
						System.out.println("La base de datos no tiene la estructura correcta.");
						
						continue;
					} else if (allMachineInfo.isEmpty()) {
						System.out.println("Ninguna maquina ha trabajado en este intervalo de tiempo.");
						
						continue;
					} else {
						for (AllInfo m: allMachineInfo)
							System.out.print(" - " + m.getMachineID());
						allMachineInfo = cleanList(allMachineInfo);
						
						
						for (AllInfo info: allMachineInfo) {
							System.out.println("\nOperaciones realizadas por la maquina "+info.getMachineID()+" en el intervalo de tiempo establecido:");
							System.out.println("-------------");
							System.out.println("MachineID: " + info.getMachineID());
							System.out.println("ActualTimes: " + info.actualTimesToString());
							System.out.println("PlannedTimes: " + info.plannedTimesToString());
							System.out.println("-------------");
							
							
							JSONObject jsonAux = info.getJSON();
							machinesArray.add(jsonAux);
						}
						
						json.put("machines", machinesArray);
						
						machineWorking = true;
					}
				}

	            // Le añadimos el rango de tiempo del que hemos cogido los datos
				json.put("range", rangeMinute);
	            json.put("start", horaInicio);
	            json.put("finish", horaFin);
				
				System.out.println("JSON:\n" + json);
				
				// Teniendo todos los datos para el calulo del OEE, se los enviaremos al PQP (Proc Quality Performance) para que lo calcule
				
				// Solo enviaremos si ha conseguido algun dato
				if (machineWorking == true) {
					
					// Teniendo todos los datos, los publicaremos en Kafka
					String topic = "topico-datos-oee";	// TODO es este el topico? Donde se define? Viene dado en una variable de entorno?
					String key = "sde-1";	// TODO Aquí habría que añadirlo por variable de entorno (diseñado por el usuario, dependiendo de la aplicacion, p.e. app1-getassemblystation)
					publishDataKafka(topic, key, json);
				
					
					// TODO Envio directo version vieja
//					String pqpURL = "http://" + output + ":6000/calculate/";
//					URL url = new URL(pqpURL);
//		            System.out.println("--> Sending machine data to PQP : " + url);
//		            HttpURLConnection connect = (HttpURLConnection) url.openConnection();
//		            connect.setRequestMethod("POST");
//		            connect.setDoOutput(true);
//		            
//		            connect.setRequestProperty("Content-Type", "application/json");
//		            connect.setRequestProperty("Content-Length", Integer.toString(json.toString().length()));
//		            try (DataOutputStream wr = new DataOutputStream(connect.getOutputStream())) {
//		                wr.write(json.toString().getBytes(StandardCharsets.UTF_8));
//		            }
//		            
//		            int status = connect.getResponseCode();
//		            String response = connect.getResponseMessage();
//		            System.out.println("   <-- Status: " + status);
//		            System.out.println("   <-- Response Message: " + response);
	            
				}
	            
				
				
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
	}

	private static void connectToeXist() throws Exception {
        // Method to connect with eXist-DB

        try {
            Class existDriver = Class.forName("org.exist.xmldb.DatabaseImpl");
            Database database = (Database) existDriver.newInstance();
            database.setProperty("create-database", "true"); //Creates a new local instance
            DatabaseManager.registerDatabase(database);

            System.out.println(eXistName + " DATABASE DRIVER INITIALIZED");

            String URI = "xmldb:exist://" +eXistName+ ":8080/exist/xmlrpc/db";
            dbCollection = DatabaseManager.getCollection(URI, "admin", "");	// TODO mirar de donde conseguir el usuario y contrasena

            System.out.println("DATABASE CONNECTION");

            // Sometimes, although the connection to the database is wrong, there is not an exception until
            // a collection is tried to be accessed
            // Therefore, to be sure, an action with the root collection is executed.
            int i = dbCollection.getChildCollectionCount();
//            System.out.println("Child collection count --> " + i);	
//            System.out.println("DATABASE FIRST QUERY");

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
	
	
	/**
	 * Method to get only information about one specific machine
	 * @param machineID
	 * @param horaInicio
	 * @param horaFin
	 * @throws XMLDBException
	 */
	private static void getMachineInfo(String machineID, String horaInicio, String horaFin) throws XMLDBException {
		
		machineInfo = new AllInfo(machineID);
		
		Collection ordersCollection = dbCollection.getChildCollection("orders");
		if (ordersCollection == null) {
			machineInfo = null;
			return;
		}
		
		String[] allOrders = ordersCollection.listChildCollections();
		for (String order : allOrders) {
			// Por cada order hay que recorrer cada batch
			Collection orderCol = ordersCollection.getChildCollection(order);
			String[] allBatchesOfOrder = orderCol.listChildCollections();
			for (String batch: allBatchesOfOrder) {
				// Por cada batch hay que recorrer cada item
				Collection batchCol = orderCol.getChildCollection(batch);
				String[] allItemsOfBatch = batchCol.listResources();
				for (String item: allItemsOfBatch) {
					// Ahora, guardaremos cada accion en la informacion de la maquina
					Document xmlFile = (Document) ((XMLResource) batchCol.getResource(item)).getContentAsDOM();
					System.out.println("Analyzing item " + item + " on batch " + batch + " on order " + order + "...");
					NodeList allActions = xmlFile.getElementsByTagName("action");
					
					Node itemNode = xmlFile.getElementsByTagName("item").item(0);
					Element itemElem = (Element) itemNode;
					String itemID = itemElem.getAttribute("item_ID");
					
					for (int temp = 0; temp < allActions.getLength(); temp++) {
						Node actionNode = allActions.item(temp);
	    		        if (actionNode.getNodeType() == Node.ELEMENT_NODE) {
	    		            Element actionElem = (Element) actionNode;
	    		            
	    		            // Solo vamos a analizar las acciones de la maquina deseada
	    		            if (machineID.equals(actionElem.getAttribute("actualMachineId"))) {
	    		            	// Quito la fecha y me quedo solo con las horas
		    		            String plannedStartTime = actionElem.getAttribute("plannedStartTime").split(" ")[1];
		    		            String plannedFinishTime = actionElem.getAttribute("plannedFinishTime").split(" ")[1];
		    		            String actualStartTime = actionElem.getAttribute("actualStartTime").split(" ")[1];
		    		            String actualFinishTime = actionElem.getAttribute("actualFinishTime").split(" ")[1];
		    		            String actionID = actionElem.getAttribute("id");
		    		            
		    		            if ((plannedStartTime !=null) && (actualStartTime != null)) {
	
		    		            	// Solo vamos a guardar si existen los dos datos: planeado y real
		    		            	if ((hourIsBefore(actualStartTime, horaInicio) && (hourIsBefore(horaInicio, actualFinishTime))))
		    		            		// Si el actual esta medio-dentro por el principio, es decir, su startTime es antes del inicio y el finishTime despues
		    		            		machineInfo = addMachineData(machineInfo, machineID, itemID, actionID, actualStartTime, actualFinishTime, plannedStartTime, plannedFinishTime);
		    		            	else if ((hourIsBefore(horaInicio, actualStartTime)) && (hourIsBefore(actualFinishTime, horaFin)))
		    		        			// Si el actual esta dentro
		    		            		machineInfo = addMachineData(machineInfo, machineID, itemID, actionID, actualStartTime, actualFinishTime, plannedStartTime, plannedFinishTime);
		    		            	else if ((hourIsBefore(actualStartTime, horaFin)) && (hourIsBefore(horaFin, actualFinishTime)))
		    		        			// Si el actual esta medio-dentro por el final, es decir, su startTime es antes del final y el finishTime despues
		    		            		machineInfo = addMachineData(machineInfo, machineID, itemID, actionID, actualStartTime, horaFin, null, null);
		    		            	// Si esta fuera del intervalo, me olvido
		    		            }
	    		            }
	    		            
	    		        }
					}
					
				}
			}
		}
		
	}
	
	
	/**
	 * Method to get information about all machines
	 * @param horaInicio
	 * @param horaFin
	 * @throws XMLDBException
	 */
	private static ArrayList<AllInfo> getAllMachineInfo(String horaInicio, String horaFin, String fecha) throws XMLDBException {
		
		ArrayList<AllInfo> allInfoList = new ArrayList<AllInfo>();
		//machineInfo = new AllInfo(machineID);
		
		Collection ordersCollection = dbCollection.getChildCollection("orders");
		if (ordersCollection == null) {
			machineInfo = null;
			return null;
		}
		
		String[] allOrders = ordersCollection.listChildCollections();
		for (String order : allOrders) {
			// Por cada order hay que recorrer cada batch
			Collection orderCol = ordersCollection.getChildCollection(order);
			String[] allBatchesOfOrder = orderCol.listChildCollections();
			for (String batch: allBatchesOfOrder) {
				// Por cada batch hay que recorrer cada item
				Collection batchCol = orderCol.getChildCollection(batch);
				String[] allItemsOfBatch = batchCol.listResources();
				for (String item: allItemsOfBatch) {
					// Ahora, guardaremos cada accion en la informacion de la maquina
					Document xmlFile = (Document) ((XMLResource) batchCol.getResource(item)).getContentAsDOM();
					System.out.println("Analyzing item " + item + " on batch " + batch + " on order " + order + "...");
					NodeList allActions = xmlFile.getElementsByTagName("action");
					
					Node itemNode = xmlFile.getElementsByTagName("item").item(0);
					Element itemElem = (Element) itemNode;
					String itemID = itemElem.getAttribute("item_ID");
					
					for (int temp = 0; temp < allActions.getLength(); temp++) {
						Node actionNode = allActions.item(temp);
	    		        if (actionNode.getNodeType() == Node.ELEMENT_NODE) {
	    		            Element actionElem = (Element) actionNode;
	    		            
	    		           
	    		            	
    		            	// Quito la fecha y me quedo solo con las horas

	    		            String plannedStartTime = actionElem.getAttribute("plannedStartTime").split(" ")[1];
	    		            String actualStartTime = actionElem.getAttribute("actualStartTime").split(" ")[1];
	    		            
	    		            String actualDate = actionElem.getAttribute("actualStartTime").split(" ")[0];
	    		            
	    		            if (actualDate.equals(fecha)) {
	    		            	
	    		            	// Solo vamos a analizar las acciones realizadas en el mismo dia que se ejecuta la aplicacion
	    		            
		    		            if ((plannedStartTime !=null) && (actualStartTime != null)) {
		
		    		            	// Solo vamos a guardar si existen los dos datos: planeado y real
		    		            	String machineID = actionElem.getAttribute("actualMachineId");
			    		            String plannedFinishTime = actionElem.getAttribute("plannedFinishTime").split(" ")[1];
			    		            String actualFinishTime = actionElem.getAttribute("actualFinishTime").split(" ")[1];
			    		            String actionID = actionElem.getAttribute("id");
		    		            	
		    		            	
			    		            AllInfo machineObject = getMachineObject(allInfoList, machineID);
			    		            if (machineObject == null)
			    		            	machineObject = new AllInfo(machineID);
		    		            	
		    		            	
		    		            	if ((hourIsBefore(actualStartTime, horaInicio) && (hourIsBefore(horaInicio, actualFinishTime))))
		    		            		// Si el actual esta medio-dentro por el principio, es decir, su startTime es antes del inicio y el finishTime despues
		    		            		machineObject = addMachineData(machineObject, machineID, itemID, actionID, actualStartTime, actualFinishTime, plannedStartTime, plannedFinishTime);
		    		            	else if ((hourIsBefore(horaInicio, actualStartTime)) && (hourIsBefore(actualFinishTime, horaFin)))
		    		        			// Si el actual esta dentro
		    		            		machineObject = addMachineData(machineObject, machineID, itemID, actionID, actualStartTime, actualFinishTime, plannedStartTime, plannedFinishTime);
		    		            	else if ((hourIsBefore(actualStartTime, horaFin)) && (hourIsBefore(horaFin, actualFinishTime)))
		    		        			// Si el actual esta medio-dentro por el final, es decir, su startTime es antes del final y el finishTime despues
		    		            		machineObject = addMachineData(machineObject, machineID, itemID, actionID, actualStartTime, horaFin, null, null);
		    		            	// Si esta fuera del intervalo, me olvido
		    		            	
		    		            	if (allInfoList.contains(machineObject))
		    		            		allInfoList.remove(machineObject);
		    		            	allInfoList.add(machineObject);
		    		            }
	    		            }
	    		            
	    		        }
					}
					
				}
			}
		}
		
		return allInfoList;
	}
	


	private static AllInfo addMachineData(AllInfo machineObject, String machineID, String itemID, String actionID, String actualStart, String actualFinish,
			String plannedStart, String plannedFinish) {
		
		String itemActionID = timeIsRepeated(machineObject, itemID, actualStart, actualFinish);
		if (itemActionID != null) {
			machineObject.updateActualAction(itemID, actionID, itemActionID);
			machineObject.updatePlannedAction(itemID, actionID, itemActionID);
			return machineObject;
		}
		
		if (plannedStart != null)	
			machineObject.addNewPlannedTime(itemID + ":"+ actionID, plannedStart + "&" + plannedFinish);
		else
			machineObject.addNewPlannedTime(itemID + ":"+ actionID, "");
		machineObject.addNewActualTime(itemID + ":"+ actionID, actualStart + "&" + actualFinish);
		
		return machineObject;
	}


	private static String timeIsRepeated(AllInfo machineInfo, String itemID, String actualStart, String actualFinish) {

		Iterator it = machineInfo.getActualTimes().entrySet().iterator();
		while (it.hasNext()) {
	    	Map.Entry pair = (Map.Entry)it.next();
	    	if (pair.getValue().toString().equals(actualStart+"&"+actualFinish)) {
	    		if (pair.getKey().toString().split(":")[0].equals(itemID))	// Si coincide el tiempo y el itemID, es que hay dos acciones en ese item que se han realizado en una misma operacion
	    			return (String) pair.getKey();
	    	}
	    }
		
		return null;
	}
	
	
	private static boolean hourIsBefore(String hour1, String hour2) {
		
		try {
			Date date1 = new SimpleDateFormat("HH:mm:ss").parse(hour1);
			Date date2 = new SimpleDateFormat("HH:mm:ss").parse(hour2);
			
			return date1.before(date2);
		} catch (ParseException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		return false;
	}
	
	
	private static AllInfo getMachineObject(ArrayList<AllInfo> machineList, String machineID) {
		for (AllInfo machineInfo: machineList) {
			if (machineInfo.getMachineID().equals(machineID))
				return machineInfo;
		}
		return null;
	}
	
	private static ArrayList<AllInfo> cleanList(ArrayList<AllInfo> allMachineInfo) {
		ArrayList<AllInfo> machinesToRemove = new ArrayList<>();
		// Get machines that are empty
		for (AllInfo info: allMachineInfo) {
			if (info.getActualTimes().isEmpty())
				machinesToRemove.add(info);
		}
		
		// Remove these machines
		for (AllInfo machine: machinesToRemove) {
			allMachineInfo.remove(machine);
		}
		
		return allMachineInfo;
	}
	
	private static String publishDataKafka(String topic, String key, JSONObject data) {
		
		Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, Kafka_server + ":9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "1");
        
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, data.toString());
		
		//Sending message to Kafka Broker
		producer.send(record);
		producer.flush();
		producer.close();
		return "OK";
	}

}
