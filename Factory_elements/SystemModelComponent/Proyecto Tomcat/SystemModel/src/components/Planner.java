package components;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import utilities.XMLReader;

public class Planner {
	
	// Singleton pattern
    private static Planner instance = new Planner();
    
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
        
        // Primero registramos cada componente. Asi, se validaran las definiciones de cada componente
        for (int i = 0; i < xmlelements.size(); i++) {
			if (xmlelements.get(i).get(0).get(0).equals("componentInstance")) {
				
				attributes.clear();
				
				for (int j = 0; j < xmlelements.get(i).get(1).size(); j++) {
					attributes.put(xmlelements.get(i).get(1).get(j), xmlelements.get(i).get(2).get(j));
				}
				
				String commandSeReg = "seregister seType=" + xmlelements.get(i).get(0).get(0);
                for (Map.Entry<String, String> entry : attributes.entrySet()) {
                    commandSeReg = commandSeReg+" "+entry.getKey()+"="+entry.getValue();
                }
                
                // TODO: Una vez se tenga el mensaje de registro, se mandará al SystemModel para que lo valide (mire si existe ese tipo de componente, jerarquia, etc.)
                
				try {
					ID = SystemModel.getInstance().seRegister(commandSeReg);
				} catch (Exception e) {
					e.printStackTrace();
				}		// TODO: Más adelante el Planner estará separado del System Model y habra que cambiar este apartado para que le mande la informacion
                
                if (ID == null)
                	return "ERROR: The definition of the component with name " + attributes.get("name") + "is not the correct one, repeat the action please.\n";
                else {
                	componentsID.put(attributes.get("name"), ID);
                	System.out.println("Component " + ID + " registered.");
                }
                
			}
		}
        
        // Despues, si todos los componentes son correctos, se validaran las conexiones entre ellos, es decir, se registrarán los canales
        for (int i = 0; i < xmlelements.size(); i++) {
        	if (xmlelements.get(i).get(0).get(0).equals("channel")) {
        		
        		attributes.clear();
        		
        		for (int j = 0; j < xmlelements.get(i).get(1).size(); j++) {
					attributes.put(xmlelements.get(i).get(1).get(j), xmlelements.get(i).get(2).get(j));
				}
        		
        		String commandSeReg = "seregister seType=" + xmlelements.get(i).get(0).get(0);
        		commandSeReg = commandSeReg + " from=" + componentsID.get(attributes.get("from").split("::")[0]) + " fromPort=" + attributes.get("from").split("::")[1];
        		commandSeReg = commandSeReg + " to=" + componentsID.get(attributes.get("to").split("::")[0]) + " toPort=" + attributes.get("to").split("::")[1];
        		commandSeReg = commandSeReg + " link=" + attributes.get("link");
        		
				try {
					ID = SystemModel.getInstance().seRegister(commandSeReg);
				} catch (Exception e) {
					e.printStackTrace();
				}		// TODO: Más adelante el Planner estará separado del System Model y habra que cambiar este apartado para que le mande la informacion
                
                if (ID == null)
                	return "ERROR: The definition of the channel between " + attributes.get("from").split("::")[0] + " and " + attributes.get("to").split("::")[0]+ " is not the correct one, repeat the action please.\n";
                else {
                	channelsID.put(componentsID.get(attributes.get("from").split("::")[0]) + ">" + componentsID.get(attributes.get("to").split("::")[0]), ID);
                	System.out.println("Channel " + ID + " registered.");
                }
                
        	}
        }
        
        
        
        // Si todos los componentes y los canales son correctos, se registrara la aplicacion en systemModel
        String commandAppReg = "appregister components=";
        for (String component : componentsID.values())
			commandAppReg = commandAppReg + component + ",";
        
        commandAppReg = commandAppReg.substring(0, commandAppReg.length()-1) + " channels=";
        for (String channel : channelsID.values())
        	commandAppReg = commandAppReg + channel + ",";
        
        commandAppReg = commandAppReg.substring(0, commandAppReg.length()-1);
        try {
			ID = SystemModel.getInstance().appRegister(commandAppReg);
		} catch (Exception e) {
			e.printStackTrace();
		}		// TODO: Más adelante el Planner estará separado del System Model y habra que cambiar este apartado para que le mande la informacion
    	
    	return ID;
    }
    

}
