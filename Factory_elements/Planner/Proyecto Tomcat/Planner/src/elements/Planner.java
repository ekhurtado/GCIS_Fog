package elements;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import utilities.XMLReader;

public class Planner {
	
	// Singleton pattern
    private static Planner instance = new Planner();
    
    private String systemModelURL = "http://system-model:8080/SystemModel/";
    private String eventManagerURL = "http://event-manager:8080/EventManager/";
    
    private Planner() {

    }

    public static Planner getInstance() {
        return instance;
    }
    
    
    public String appRegister(String appDefinition) {
    	    	
		ConcurrentHashMap<String, String> attributes = new ConcurrentHashMap<String, String>();
		ArrayList<ArrayList<ArrayList<String>>> xmlelements = new ArrayList<>();
        try {
        	xmlelements = XMLReader.readFile(appDefinition);
        } catch (Exception e) {
            System.out.println("\nSorry, but the XML definition is not the correct one, repeat the action please.\n");
            return null;
        }
        
        HashMap<String, String> componentsID = new HashMap<>();
        HashMap<String, String> channelsID = new HashMap<>();
        String ID = null;
//        systemModelURL = "http://192.168.233.131:30800/SystemModel/";
        
        // Primero registramos cada componente. Asi, se validaran las definiciones de cada componente
        for (int i = 0; i < xmlelements.size(); i++) {
			if (xmlelements.get(i).get(0).get(0).equals("componentInstance")) {
				
				attributes = new ConcurrentHashMap<String, String>();
				
				for (int j = 0; j < xmlelements.get(i).get(1).size(); j++) {
					attributes.put(xmlelements.get(i).get(1).get(j), xmlelements.get(i).get(2).get(j));
				}
				
				String commandSeReg = "seregister seType=" + xmlelements.get(i).get(0).get(0);
                for (Map.Entry<String, String> entry : attributes.entrySet()) {
                    commandSeReg = commandSeReg+" "+entry.getKey()+"="+entry.getValue();
                }
                
                // TODO: Una vez se tenga el mensaje de registro, se mandará al SystemModel para que lo valide (mire si existe ese tipo de componente, jerarquia, etc.)
                
				try {
//					ID = SystemModel.getInstance().seRegister(commandSeReg);
					ID = sendHTTPMessage(systemModelURL + "register/systemElement", commandSeReg, "application/text", null);
				} catch (Exception e) {
					e.printStackTrace();
				}
                
                if ((ID == null) || (ID.contains("ERROR"))) {	// Como a partir de ahora van a ser mensaje HTTP entre Planner y SystemModel hay que comprobar si el mensaje que devuelve es "null" if (ID.equals("null"))
                	deletePreviousElements(componentsID);
                	return "ERROR: The definition of the component with name " + attributes.get("name") + " is not the correct one, repeat the action please. \nMessage: "+ID+"\n";
                } else {
                	componentsID.put(attributes.get("name"), ID);
                	System.out.println("Component " + ID + " registered.");
                }
                
			}
		}
		
        // Despues, si todos los componentes son correctos, se validaran las conexiones entre ellos, es decir, se registrarán los canales
        for (int i = 0; i < xmlelements.size(); i++) {
        	if (xmlelements.get(i).get(0).get(0).equals("channel")) {
        		
        		attributes = new ConcurrentHashMap<String, String>();
        		
        		for (int j = 0; j < xmlelements.get(i).get(1).size(); j++) {
					attributes.put(xmlelements.get(i).get(1).get(j), xmlelements.get(i).get(2).get(j));
				}
        		
        		String commandSeReg = "seregister seType=" + xmlelements.get(i).get(0).get(0);
        		commandSeReg = commandSeReg + " from=" + componentsID.get(attributes.get("from").split("::")[0]) + " fromPort=" + attributes.get("from").split("::")[1];
        		commandSeReg = commandSeReg + " to=" + componentsID.get(attributes.get("to").split("::")[0]) + " toPort=" + attributes.get("to").split("::")[1];
        		commandSeReg = commandSeReg + " link=" + attributes.get("link");
        		
				try {
//					ID = SystemModel.getInstance().seRegister(commandSeReg);
					ID = sendHTTPMessage(systemModelURL + "register/systemElement", commandSeReg, "application/text", null);
				} catch (Exception e) {
					e.printStackTrace();
				}
                
                if ((ID == null) || (ID.contains("ERROR"))) {
                	deletePreviousElements(channelsID);
                	return "ERROR: The definition of the channel between " + attributes.get("from").split("::")[0] + " and " + attributes.get("to").split("::")[0]+ " is not the correct one, repeat the action please. \nMessage: "+ID+"\n";
                } else {
                	channelsID.put(componentsID.get(attributes.get("from").split("::")[0]) + ">" + componentsID.get(attributes.get("to").split("::")[0]), ID);
                	System.out.println("Channel " + ID + " registered.");
                }
                
        	}
        }
        
        // Si todos los componentes y los canales son correctos, se validará la aplicacion al completo
        String result = "";
        try {
//			ID = SystemModel.getInstance().seRegister(commandSeReg);
			result = sendHTTPMessage(systemModelURL + "validate/application", appDefinition, "application/xml", null);
		} catch (Exception e) {
			e.printStackTrace();
		}
        
        if (!result.equals("valid")) {
        	deletePreviousElements(componentsID);
        	deletePreviousElements(channelsID);
        	return "ERROR: The definition of the application is not valid: " + result;
        } else
        	System.out.println("Application is valid.");
        
        // Si todos los componentes y los canales son correctos, se registrara la aplicacion en systemModel
        String commandAppReg = "appregister components=";
        for (String component : componentsID.values())
			commandAppReg = commandAppReg + component + ",";
        
        commandAppReg = commandAppReg.substring(0, commandAppReg.length()-1) + " channels=";
        for (String channel : channelsID.values())
        	commandAppReg = commandAppReg + channel + ",";
        
        commandAppReg = commandAppReg.substring(0, commandAppReg.length()-1);
        try {
//			ID = SystemModel.getInstance().appRegister(commandAppReg);
			ID = sendHTTPMessage(systemModelURL + "register/application", commandAppReg, "application/text", null);
		} catch (Exception e) {
			e.printStackTrace();
		}		// TODO: Más adelante el Planner estará separado del System Model y habra que cambiar este apartado para que le mande la informacion
    	
        System.out.println("Application " + ID + " registered.");
        
        // Despues de registrar la aplicacion, vamos a crearla
        if (!ID.contains("ERROR")) {
        	
        	String startResult = null;
        	try {
        		startResult = sendHTTPMessage(systemModelURL + "start/application", ID, "application/text", null);
    		} catch (Exception e) {
    			e.printStackTrace();
    		}
        	
        	if (startResult.contains("ERROR"))
        		return "ERROR: The application could not be started: " + startResult;
        	
//        	System.out.println("DOCKER COMPOSE FILE:");
//        	System.out.println(startResult);
//        	
//        	// TODO Borrar
//        	System.out.println("Docker compose con \\n");
//        	String aa =  startResult.replace("\n", "\\n");
//        	System.out.println("\n" + aa);
//        	
//        	if (!startResult.contains("ERROR")) {
//        		System.out.println("Sending docker compose file to Event Manager...");
//        		try {
//        			// startResult is the definition of the docker compose file
//        			result = sendHTTPMessage(eventManagerURL + "deploy/application", startResult, "application/x-yml", "applicationID=" + ID);
//        		} catch (Exception e) {
//        			e.printStackTrace();
//        		}
//        		
//        		
//        	} else
//        		return result;
        }
        
    	return ID;
    }
   

	private String sendHTTPMessage(String urlString, String content, String type, String newHeader) throws Exception {
    	
    	URL url = new URL(urlString);
    	HttpURLConnection connect = (HttpURLConnection) url.openConnection();
        connect.setRequestMethod("POST");
        connect.setDoOutput(true);
        
        if (newHeader !=null) {
        	System.out.println("New header in the message to " + urlString + ": " + newHeader);
        	String headerName = newHeader.split("=")[0];
        	String headerValue = newHeader.split("=")[1];
        	connect.setRequestProperty(headerName, headerValue);
        }
        
        connect.setRequestProperty("Content-Type", type);
        connect.setRequestProperty("Content-Length", Integer.toString(content.toString().length()));
        try (DataOutputStream wr = new DataOutputStream(connect.getOutputStream())) {
            wr.write(content.getBytes(StandardCharsets.UTF_8));
        }
        
        System.out.println("Message to " + urlString + " with the content: " + content);
        String responseMessage = getResponseMessage(connect);
        System.out.println("   <-- Response Message: " + responseMessage);
        
        return responseMessage;
	}
	
	

	private String getResponseMessage(HttpURLConnection connect) throws IOException {

		InputStream is = connect.getInputStream();
	    BufferedReader rd = new BufferedReader(new InputStreamReader(is));
	    StringBuilder response = new StringBuilder();
//	    String line;
//	    while ((line = rd.readLine()) != null) {
//	      response.append(line);
//	    }
//	    rd.close();
	    
	    char[] buf = new char[4096];
	    int size = 0;
	    while((size = rd.read(buf)) != -1) {
	        String someString = new String(buf, 0, size);
	        response.append(someString);
	    }
	    
//	    while((value = br.read()) != -1) {
//	         
//            // converts int to character
//            char c = (char)value;
//            
//            // prints character
//            System.out.println(c);
//         }
	    
	    
	    return response.toString();
	}
	
	private void deletePreviousElements(HashMap<String, String> list) {
		
		for (String componentID : list.values()) {
			try {
				sendHTTPMessage(systemModelURL + "delete", componentID, "application/text", null);
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
		
	}
    

}
