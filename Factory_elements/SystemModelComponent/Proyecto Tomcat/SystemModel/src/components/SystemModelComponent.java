package components;

import java.util.ArrayList;

import java.util.Hashtable;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import models.Component;
import models.DockerCompose;

public class SystemModelComponent {
	
//	private static ConcurrentHashMap<String, Hashtable<String, String>> elements = new ConcurrentHashMap<String, Hashtable<String, String>>();
	private static ConcurrentHashMap<String, ArrayList<Component>> elements = new ConcurrentHashMap<String, ArrayList<Component>>();
	
	private static ConcurrentHashMap<String, Integer> count = new ConcurrentHashMap<String, Integer>();
	
	private static ArrayList<Component> componentsFlow = new ArrayList<>();
	
	// TODO Borrar
	private static ArrayList<String> typeOfElements = new ArrayList<>();
	
	public SystemModelComponent() {
		// TODO Auto-generated constructor stub
	}
	
	public static String seRegister(String cmd, String seType) {
		
		// TODO Borrar: Prueba para Nodered
		typeOfElements.add("application");
		typeOfElements.add("event");
		
		/////////////////////////////////////////
		// 1. Extraer la informacion de la peticion
		JSONParser parser = new JSONParser();
		JSONObject jsonObject = null;
		try {
			jsonObject = (JSONObject) parser.parse(cmd);
		} catch (ParseException e) {
			System.out.println("Error parsing JSON.");
			e.printStackTrace();
		}
		
		// Convert JSON object to a list of Component objects
		componentsFlow = jsonToList(jsonObject);
		
		// TODO Borrar
		for (Component component : componentsFlow) {
			System.out.println(component.toString());
		}
		
		System.out.println("\n-----> seType: " + seType);
		
		/////////////////////////////////////////
		// 2. Comprobar si el elemento existe
		if (!typeOfElements.contains(seType)) {
			System.err.println("Type not found");
			return null;
		}
		
		/////////////////////////////////////////
		// 3. Validar la definicion de cada componente
		for (Component component : componentsFlow) {
			if (componentIsValid(component) == false) {
				System.err.println("Component " +component+ " is not valid.");
				return null;
			}
		}
		
		/////////////////////////////////////////
		// 4. Validar la consistencia de la aplicacion en su conjunto
		if (flowIsValid() == false) {
			System.err.println("Application flow is not valid.");
			// TODO borrar comentario: quitado para pruebas
			return null;
		}
		
		/////////////////////////////////////////
		// 5. Registrar el nuevo elemento
		
		String ID = reg(seType);
		
		
		// Devuelve el ID del nuevo elemento
		return ID;
	}

	public static String reg(String seType) {
		
		String id = "";
		
		// Genero un ID
		id = seType.toLowerCase();
		if (!count.containsKey(id)) count.put(id, 1);
        else count.put(id, (count.get(id)) + 1);
        id = id + count.get(id);
		
        elements.put(id, componentsFlow);
        System.out.println("New " + seType + " registered.");
        
		return id;
	}
	
	
	public static String listElements() {
		StringBuilder sb = new StringBuilder();
		for (String key : elements.keySet()) {
			sb.append("\t" + key + ":\n");
			Iterator<Component> it = elements.get(key).iterator();
			while (it.hasNext()) {
			  Component entry = it.next();
			  sb.append("\t\t   - " + entry + "\n");
			}
		}
		
		return sb.toString();
	}
	
	public static String listTypes() {
		StringBuilder sb = new StringBuilder();
		for (String string : typeOfElements) {
			sb.append("\t" + string + "\n");
		}
		
		return sb.toString();
	}
	
	public static void regType(String type) {
		typeOfElements.add(type);
	}

	private static Hashtable<String, String> processAttribs(String[] cmdLine) {
		
		Hashtable<String, String> attribs = new Hashtable<>();
		
		for (String aux : cmdLine) {
			attribs.put(aux.split("=")[0], aux.split("=")[1]);
		}
		return attribs;
	}
	
	//////////////////////////////
	// Flow methods
	//////////////////////////////
	private static Component getComponentByNumber(int number) {
		for (Component component : componentsFlow) {
			if (component.getPositionInFlow() == number)
				return component;
		}
		
		return null;
	}
	
	
	//////////////////////////////
	// Register methods
	//////////////////////////////
	
	private static ArrayList<Component> jsonToList(JSONObject jsonObject) {
		
		ArrayList<Component> list = new ArrayList<>();
		
		for (Object key : jsonObject.keySet()) {
	        String keyStr = (String) key;
	        JSONObject componentJSON = (JSONObject) jsonObject.get(keyStr);
	        Component newComponent = new Component((int) Integer.parseInt((String) componentJSON.get("POSITION")), (String) componentJSON.get("FROM"), (String) componentJSON.get("CMD"));
	        
	        int i = 1;
	        while (componentJSON.get("ENV" + i) != null) {
	        	String envStr = (String) componentJSON.get("ENV" + i);
	        	newComponent.addEnvVariable(envStr.split("=")[0], envStr.split("=")[1]);
	        	i++;
	        }
	        list.add(newComponent);
	    }
		
		return list;
	}
	
	//////////////////////////////
	// Validation methods
	//////////////////////////////
	
	private static boolean componentIsValid(Component component) {
		
		boolean isValid = true;
		
		// TODO develop method
		
		return isValid;
	}
	
	private static boolean flowIsValid() {
		
		int pos = 1;
		
		while (pos < componentsFlow.size()) {
			Component actualComp = getComponentByNumber(pos);
			Component nextComp = getComponentByNumber(pos + 1);
			
			String outPort = actualComp.getEnvVariable("outPort");
			String inPort = nextComp.getEnvVariable("inPort");
			
			System.out.println("Ports:");
			System.out.println("\t" + actualComp.getBaseImage() + " outPort: " + outPort);
			System.out.println("\t" + nextComp.getBaseImage() + " inPort: " + inPort);
			
			// The ports must be the same
			if (!outPort.equals(inPort))
				return false;
			
			pos ++;
		}
		
		return true;
		
	}
	

}
