package appfil2;


import java.io.DataOutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;

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


public class SDE {
	
	// SDE --> Source Datos Estaciones
	
	// eXist variables
    private static String serverExist = "http://exist:8080";
    private static String eXistName = "exist";
    private static Collection dbCollection = null;  // Root collection of the repository

    //Error Messages
    private static final String PERMISSION_DENIED_EXCEPTION = "org.exist.security.PermissionDeniedException";
    private static final String PERMISSION_DENIED_EXCEPTION_MESSAGE = "Permission denied";

    private static AllInfo machineInfo = null;
    
	public static void main(String[] args) {
		
		// Primero se va a conectar a la BBDD eXist
		try {
			connectToeXist();
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		
		// Ahora, cada 15 minutos, analizara la base de datos, y guardara el calculo del analisis
		while(true) {
			try {
				Thread.sleep(60000);	// 1 minuto
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			// Cogemos las variables de entorno con las que se modela la aplicacion
			String machineID = System.getenv("MACHINE_ID");
			String pqpName = System.getenv("PQP_NAME");
			int rangeMinute = Integer.parseInt(System.getenv("RANGE"));
			int range = rangeMinute * 60000;	// Como el range nos los van a pasar en minutos, hay que pasarlo a milisegundos

			Date date = new Date();
			DateFormat hourFormat = new SimpleDateFormat("HH:mm:ss");
			hourFormat.setTimeZone(TimeZone.getTimeZone("Europe/Madrid"));
			String horaFin = hourFormat.format(date);

			date.setTime(date.getTime()- range);
			String horaInicio = hourFormat.format(date);
			
			// TODO: Borrar ES PARA PRUEBAS!!!
			horaInicio = "11:15:00";
			horaFin = "12:15:00";

			System.out.println("-----------------> Intervalo de tiempo: "+horaInicio+" - " + horaFin);

			// Recorrera toda la BBDD guardando todos los datos de la maquina deseada
			try {
				getMachineInfo(machineID, horaInicio, horaFin);
				
				if (machineInfo == null)
					System.out.println("La base de datos no tiene la estructura correcta.");
				else if ((machineInfo.getActualTimes().isEmpty()))
					System.out.println("Esta maquina no ha trabajado en este intervalo de tiempo.");
				else {
					System.out.println("Operaciones realizadas por la maquina "+machineID+" en el intervalo de tiempo establecido:");
					System.out.println("-------------");
					System.out.println("MachineID: " + machineInfo.getMachineID());
					System.out.println("ActualTimes: " + machineInfo.actualTimesToString());
					System.out.println("PlannedTimes: " + machineInfo.plannedTimesToString());
					System.out.println("-------------");
					
					// Teniendo todos los datos de esa maquina, se los enviaremos al PQP (Proc Quality Performance) para que calcule el OEE
					
					String pqpURL = "http://" + pqpName + ":6000/calculate/"+ machineID + "/";
					URL url = new URL(pqpURL);
		            System.out.println("--> Sending machine data to PQP : " + url);
		            HttpURLConnection connect = (HttpURLConnection) url.openConnection();
		            connect.setRequestMethod("POST");
		            connect.setDoOutput(true);

		            // Vamos a crear el JSON con toda la informacion de la maquina

		            JSONObject json = machineInfo.getJSON();
		            System.out.println("JSON: " + json);
		            
		            // Le añadimos el rango de tiempo del que hemos cogido los datos
		            json.put("range", rangeMinute);
		            json.put("start", horaInicio);
		            json.put("finish", horaFin);
		            
		            connect.setRequestProperty("Content-Type", "application/json");
		            connect.setRequestProperty("Content-Length", Integer.toString(json.toString().length()));
		            try (DataOutputStream wr = new DataOutputStream(connect.getOutputStream())) {
		                wr.write(json.toString().getBytes(StandardCharsets.UTF_8));
		            }
		            
		            int status = connect.getResponseCode();
		            String response = connect.getResponseMessage();
		            System.out.println("   <-- Status: " + status);
		            System.out.println("   <-- Response Message: " + response);
		            
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
            System.out.println("Child collection count --> " + i);	
            System.out.println("DATABASE FIRST QUERY");

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
		    		            		addMachineData(machineID, itemID, actionID, actualStartTime, actualFinishTime, plannedStartTime, plannedFinishTime);
		    		            	else if ((hourIsBefore(horaInicio, actualStartTime)) && (hourIsBefore(actualFinishTime, horaFin)))
		    		        			// Si el actual esta dentro
		    		            		addMachineData(machineID, itemID, actionID, actualStartTime, actualFinishTime, plannedStartTime, plannedFinishTime);
		    		            	else if ((hourIsBefore(actualStartTime, horaFin)) && (hourIsBefore(horaFin, actualFinishTime)))
		    		        			// Si el actual esta medio-dentro por el final, es decir, su startTime es antes del final y el finishTime despues
		    		            		addMachineData(machineID, itemID, actionID, actualStartTime, horaFin, null, null);
		    		            	// Si esta fuera del intervalo, me olvido
		    		            }
	    		            }
	    		            
	    		        }
					}
					
				}
			}
		}
		
	}
	


	private static void addMachineData(String machineID, String itemID, String actionID, String actualStart, String actualFinish,
			String plannedStart, String plannedFinish) {
		
		String itemActionID = timeIsRepeated(machineInfo, itemID, actualStart, actualFinish);
		if (itemActionID != null) {
			machineInfo.updateActualAction(itemID, actionID, itemActionID);
			machineInfo.updatePlannedAction(itemID, actionID, itemActionID);
			return;
		}
		
		if (plannedStart != null)	
			machineInfo.addNewPlannedTime(itemID + ":"+ actionID, plannedStart + "&" + plannedFinish);
		else
			machineInfo.addNewPlannedTime(itemID + ":"+ actionID, "");
		machineInfo.addNewActualTime(itemID + ":"+ actionID, actualStart + "&" + actualFinish);
		
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
	
}
