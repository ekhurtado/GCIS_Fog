package components;

import java.io.BufferedInputStream;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.concurrent.ConcurrentHashMap;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Source;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.InputSource;
import org.yaml.snakeyaml.Yaml;

import io.kubernetes.client.ApiClient;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.Configuration;
import io.kubernetes.client.apis.AppsV1Api;
import io.kubernetes.client.apis.CoreV1Api;
import io.kubernetes.client.custom.IntOrString;
import io.kubernetes.client.models.V1Deployment;
import io.kubernetes.client.models.V1Service;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.KubeConfig;
import models.Component;
import utilities.ComponentCreator;
import utilities.K8sManager;

public class SystemModel {
	
	// Singleton pattern
    private static SystemModel instance = new SystemModel();
	
    // Informacion provisional (para registros, validaciones...)
    public ConcurrentHashMap<String, Hashtable<String, String>> elements = new ConcurrentHashMap<String, Hashtable<String, String>>();
    
    // Informacion validada
    public ConcurrentHashMap<String, Hashtable<String, String>> systemElements = new ConcurrentHashMap<String, Hashtable<String, String>>();
    
    // Aplicaciones
    public ConcurrentHashMap<String, Hashtable<String, ArrayList<String>>> systemApps = new ConcurrentHashMap<String, Hashtable<String,ArrayList<String>>>();
    
	
	private static ConcurrentHashMap<String, Integer> count = new ConcurrentHashMap<String, Integer>();
	
	private static ArrayList<Component> componentsFlow = new ArrayList<>();
	
	private static ConcurrentHashMap<String,HashMap<String, HashMap<String, String>>> typeOfComponents = new ConcurrentHashMap<String, HashMap<String, HashMap<String, String>>>();
	private static ArrayList<String> typeOfEvents = new ArrayList<String>();
	private static ArrayList<String> typeOfLinks = new ArrayList<String>();
	
	
	private static String volumePath = "/system_model/";
	
	private SystemModel() {

    }

    public static SystemModel getInstance() {
        return instance;
    }
	
	
	
	//////////////////////////////
	// Register methods
	//////////////////////////////
	
	public String seRegister(String request) {
		
		// TODO: Borrar, de momento esta hecho a mano
		HashMap<String, HashMap<String, String>> functions = new HashMap<>();
		HashMap<String, String> ports = new HashMap<>();
		ports.put("outPort", "TStation");
		functions.put("assemblyStationData", ports);
		ports = new HashMap<>();
		ports.put("outPort", "TTransport");
		functions.put("transportRobot", ports);
		
		// Hay que añadir tambien el comando de inicio y la imagen base de cada tipo de componente
		ports = new HashMap<>();
		ports.put("FROM", "gcr.io/clusterekaitz/source:mqtt-http");
		ports.put("CMD", "python3 subscriber.py");
		functions.put("dockerfile", ports);
		
		regComponentType("MQTT_SOURCE_HTTP", functions);
		
		functions = new HashMap<>();
		ports = new HashMap<>();
		ports.put("inPort", "TStation");
		functions.put("storeAssemblyStationData", ports);
		ports = new HashMap<>();
		ports.put("inPort", "TTransport");
		functions.put("storeTransportRobot", ports);
		
		// Hay que añadir tambien el comando de inicio y la imagen base de cada tipo de componente
		ports = new HashMap<>();
		ports.put("FROM", "gcr.io/clusterekaitz/sink:exist");
		ports.put("CMD", "catalina.sh run");
		functions.put("dockerfile", ports);
		
		regComponentType("SINK_EXIST", functions);
		
		functions = new HashMap<>();
		ports = new HashMap<>();
		ports.put("inPort", "TDBStation");
		ports.put("outPort", "TDBStationOEE");
		functions.put("processingOEE", ports);
		ports = new HashMap<>();
		ports.put("inPort", "TDBStation");
		ports.put("outPort", "TStationPerformance");
		functions.put("processingPerformance", ports);
		
		// Hay que añadir tambien el comando de inicio y la imagen base de cada tipo de componente
		ports = new HashMap<>();
		ports.put("FROM", "gcr.io/clusterekaitz/processing:station");
		ports.put("CMD", "flask run --host=0.0.0.0");
		functions.put("dockerfile", ports);
				
		regComponentType("PROCESSING_STATION", functions);
		
		regEvent("operatorAlarm");
		regLink("http");
		
		//TODO: Fin de borrar
		
		// Comienzo del metodo
		System.out.println("Asking for registering of a system element...");
		Hashtable<String, String> attribs = null;
		
		// 1. Extraer la informacion de la peticion
		// ----------------------------------------
		attribs = processAttribs(1, request.split(" "));
		
		// 2. Comprobar si el elemento existe
		// ----------------------------------
		String seType = attribs.get("seType");
		attribs.remove("seType");
		
		switch (seType) {
			case "componentInstance":
				if (!typeOfComponents.containsKey(attribs.get("type")))
					return "ERROR: Component type " +attribs.get("type")+ " does not exist.";
				break;
			case "channel":
				if (!typeOfLinks.contains(attribs.get("link")))
					return "ERROR: Link " +attribs.get("type")+ " does not exist.";
			case "event":
				
				break;
	
			default:
				break;
		}
		
//		System.out.println("Attributes: ");
//		for (Entry<String, String> entry : attribs.entrySet()) {
//			System.out.println(entry.getKey() +" --- " + entry.getValue());
//		}
		
		
		// 3. Validar la definicion de cada componente
		// -------------------------------------------
		
		// Primero, se registra (provisionalmente), para poder validarlo (en la validacion se cojen los datos del registro)
		String seRegAttribs = "";
		for (Map.Entry<String, String> entry : attribs.entrySet()) {
			seRegAttribs = seRegAttribs+" "+entry.getKey()+"="+entry.getValue();
        }
		String ID = reg(seType, attribs);
		
//		for (Entry<String, Hashtable<String, String>> entry : elements.entrySet()) {
//			System.out.println(entry.getKey() +" --- " + entry.getValue());
//		}
		
		System.out.println("ID: " + ID);
		
		// Despues, se valida el elemento
		String validation = "not valid";
		try {
			validation = validate("systemElement", seType, ID);
		} catch (Exception e) {
			del(ID);
			e.printStackTrace();
		}
		
		System.out.println("Validation: " + validation);
		
		if (!validation.equals("valid")) {
            del(ID);
            return "ERROR: " + validation;
        } else
        	return ID;
		
	}
	
	public String appRegister(String request) {
		
		System.out.println("Asking for registering of a application...");
		
		ArrayList<String> componentsIDlist = new ArrayList<>();
		ArrayList<String> channelsIDlist = new ArrayList<>();
		
		// 1. Extraer la informacion de la peticion
		// ----------------------------------------
		String[] splits = request.split(" ");
		// 2. Guardar los elementos en el objeto systemElements (informacion persistente)
		// ------------------------------------------------------------------------------
		for (String comp : splits[1].split("=")[1].split(",")) {
			componentsIDlist.add(comp);
			systemElements.put(comp, elements.get(comp));
		}
		
		for (String channel : splits[2].split("=")[1].split(",")) {
			channelsIDlist.add(channel);
			systemElements.put(channel, elements.get(channel));
		}
		
		// 3. Registrar la aplicacion
		// --------------------------
		String ID = regApp(componentsIDlist, channelsIDlist);
		
		// 4. Una vez registrada la aplicacion y añadidos los elementos al systemElements
		//    vamos a guardar toda la informacion en un archivo XML
		// ------------------------------------------------------------------------------
		try {
			saveSystemOnXML();
		} catch (Exception e) {
			e.printStackTrace();
		}
		
		System.out.println(ID + " application registered.");
		
		return ID;
	}
	
	private String reg(final String prm, Hashtable<String, String> attribs) {
        String type = prm;
        String id = "";
        if (prm.equals("componentInstance")) {
        	attribs.put("category", "component");
        	type = attribs.get("type");
        } else
        	attribs.put("category", prm);
        if (!attribs.containsKey("ID")) { // si no llega un id lo genero
//            id = (prm.length() > 10)? prm.substring(0, 10): prm;
//        	id = id.toLowerCase();
        	id = type.toLowerCase();
            if (!count.containsKey(id)) count.put(id, 1);
            else count.put(id, (count.get(id)) + 1);
            id = id + count.get(id);
        } else { // si llega lo guardo
            id = attribs.get("ID");
            attribs.remove("ID");
        }
//        attribs.put("type", type);
        elements.put(id, attribs);
        
        return id;
    }
	
	public String regApp(ArrayList<String> componentsList, ArrayList<String> channelsList) {
		String id = "application";
        if
        	(!count.containsKey(id)) count.put(id, 1);
        else
        	count.put(id, (count.get(id)) + 1);
        id = id + count.get(id);
        
        Hashtable<String, ArrayList<String>> attribs = new Hashtable<>();
        attribs.put("components", componentsList);
        attribs.put("channels", channelsList);
        
        systemApps.put(id, attribs);
        
        return id;
	}
	
	public void regComponentType(String type, HashMap<String, HashMap<String, String>> functions) {
		typeOfComponents.put(type, functions);
	}
	
	
	public void regEvent(String type) {
		typeOfEvents.add(type);
	}
	
	public void regLink(String type) {
		typeOfLinks.add(type);
	}
	
	public void registerComponent(String type) {
		typeOfComponents.put(type, new HashMap<>());
	}
	
	//////////////////////////////
	// Validation methods
	//////////////////////////////
	
	private String validate (String... _prm) throws Exception {
		
		 String output = "valid";

        if ((_prm[0].equals("systemElement")) || (_prm[0].equals("appValidation"))){ //comprueba appConcepts.xsd
        	
        	boolean appValidation = _prm[0].equals("appValidation");
        	String schemaURL = appValidation?"Application":"AppConcepts";
        	
        	String elementID = null;
        	if (!appValidation)
        		 elementID = _prm[2];
        	
        	if (_prm[1].equals("componentInstance")) {
        	
	        	Document document = listDom(_prm[2], appValidation); //segundo parámetro indica al DOM si arrastrar los IDs
	        	
	        	SchemaFactory schemaFactory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
	        	
//	            byte[] encoded = Files.readAllBytes(Paths.get("C:\\Users\\839073\\eclipse-oxygen-workspace\\SystemModel\\schemas\\"+schemaURL+".xsd"));
	            byte[] encoded = Files.readAllBytes(Paths.get(volumePath + "schemas/"+schemaURL+".xsd"));
	        	
	        	Source schemaFile = new StreamSource(new StringReader(new String(encoded, StandardCharsets.UTF_8)));
	            Schema schema = schemaFactory.newSchema(schemaFile);
	            
		         // create a Validator instance, which can be used to validate an instance document
		        Validator validator = schema.newValidator();
		        // validate the DOM tree
		        try {
		            validator.validate(new DOMSource(document));
		        } catch (Exception e) {
		            StringWriter sw = new StringWriter();
		            e.printStackTrace(new PrintWriter(sw));
		            output = sw.toString();
		        }
		        
		        // Si hay error, muestro la descripción	
		        if (output.indexOf(';') > 0)
		        	output = output.substring(output.indexOf(";") + 2, output.indexOf('\n'));
		        
		        // Una vez comprobado que tiene los atributos necesarios, comprobaremos que existen esos atributos (funcion, puerto...)

		        // Primero, comprobaremos que existe esa funcion
		        if (!typeOfComponents.get(elements.get(elementID).get("type")).containsKey(elements.get(elementID).get("function")))
		        	return "Not valid: function " + elements.get(elementID).get("function") + " does not exist.";
		        
		        // Despues, si esa funcion tiene bien los puertos
		        HashMap<String, String> ports = typeOfComponents.get(elements.get(elementID).get("type")).get(elements.get(elementID).get("function"));
		        for (Entry<String, String> entryPort : ports.entrySet()) {
					// El nombre del puerto es la mismo
					if (elements.get(elementID).get(entryPort.getKey()) == null)
						return "Not valid: The name of the port " + entryPort.getKey() + " is not the correct one.";
					// El valor del puerto es el mismo
					if (!elements.get(elementID).get(entryPort.getKey()).equals(entryPort.getValue()))
						return "Not valid: The ports are not the same (" + elements.get(elementID).get(entryPort.getKey()) + " - " + entryPort.getValue() + ")";
				}
		        
        	} else if (_prm[1].equals("channel")) {
        		
//        		System.out.println("channel fromPort: " + elements.get(elementID).get("fromPort"));
//        		System.out.println("component fromPort: " + elements.get(elements.get(elementID).get("from")).get("outPort"));
//        		System.out.println("channel toPort: " + elements.get(elementID).get("toPort"));
//        		System.out.println("component toPort: " + elements.get(elements.get(elementID).get("to")).get("inPort"));
        		
        		
        		// Comprobar si el puerto definido en el canal y en la instancia del componente es el mismo
        		if (!elements.get(elementID).get("fromPort").equals(elements.get(elements.get(elementID).get("from")).get("outPort")))
        			return "Not valid: The port is not the same on the channel and on the component instance.";
        		if (!elements.get(elementID).get("toPort").equals(elements.get(elements.get(elementID).get("to")).get("inPort")))
        			return "Not valid: The port is not the same on the channel and on the component instance.";
        		
        		// Comprobar si los puertos coinciden
        		if (!elements.get(elementID).get("fromPort").equals(elements.get(elementID).get("toPort")))
        			return "Not valid: The channel ports are different.";
        	
        	} else if (appValidation) {
        		String xmlDefinition = _prm[1];
        		
        		// Build DOM
        		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        	    factory.setNamespaceAware(true);
        	    DocumentBuilder builder = null;
        	    builder = factory.newDocumentBuilder();
        	    Document document = builder.parse(new InputSource(new StringReader(xmlDefinition)));
	        	
	        	SchemaFactory schemaFactory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
	        	
//	            byte[] encoded = Files.readAllBytes(Paths.get("C:\\Users\\839073\\eclipse-oxygen-workspace\\SystemModel\\schemas\\"+schemaURL+".xsd"));
	            byte[] encoded = Files.readAllBytes(Paths.get(volumePath + "schemas/"+schemaURL+".xsd"));
	        	
	        	Source schemaFile = new StreamSource(new StringReader(new String(encoded, StandardCharsets.UTF_8)));
	            Schema schema = schemaFactory.newSchema(schemaFile);
	            
		         // create a Validator instance, which can be used to validate an instance document
		        Validator validator = schema.newValidator();
		        // validate the DOM tree
		        try {
		            validator.validate(new DOMSource(document));
		        } catch (Exception e) {
		            StringWriter sw = new StringWriter();
		            e.printStackTrace(new PrintWriter(sw));
		            output = sw.toString();
		        }
		        
		        // Si hay error, muestro la descripción	
		        if (output.indexOf(';') > 0)
		        	output = output.substring(output.indexOf(";") + 2, output.indexOf('\n'));
        	}
        }
        
        return output;
	}
	
	private Document listDom(String _prm, boolean mostrarID) throws Exception {

        DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
        DocumentBuilder docBuilder = docFactory.newDocumentBuilder();
        Document doc = docBuilder.newDocument();

        for (String element: elements.keySet()) {
            if (element.matches(_prm)) {

                // Genero elememto raiz del DOM
                Element rootElement = doc.createElement(elements.get(element).get("category"));
                doc.appendChild(rootElement);

                Attr attr = null;

                if (mostrarID) {
                    attr = doc.createAttribute("ID");
                    attr.setValue(element);
                    rootElement.setAttributeNode(attr);
                }

                //añado atributos al raiz
                forKeys: for (String key : elements.get(element).keySet()) {
                    if (key.equals("category") || key.equals("xsd")|| key.equals("seParent")) continue forKeys;
                    attr =  doc.createAttribute(key);
                    attr.setValue(elements.get(element).get(key));
                    rootElement.setAttributeNode(attr);
                }

                appendChildren(doc, rootElement, element, mostrarID);

            }
        }
        
        return doc;
    }
	
	private void appendChildren(Document doc, Element parent, String parentID, boolean mostrarID) {

        for (String key : elements.keySet()) {
            for (String key2 : elements.get(key).keySet()) {
                if (key2.equals("parent") && elements.get(key).get(key2).equals(parentID)) {

                    Element hijo = doc.createElement(elements.get(key).get("category"));
                    parent.appendChild(hijo);

                    boolean ocutarIDHastaCambiarXSD = elements.get(key).get("category").startsWith("restriction");

                    //TODO Aintzane: Ampliar ID a restriction en AppValidation

                    if (mostrarID && !ocutarIDHastaCambiarXSD)  {
                        Attr attr = doc.createAttribute("ID");
                        attr.setValue(key);
                        hijo.setAttributeNode(attr);
                    }

                    forKeys: for (String eachKey : elements.get(key).keySet()) {
                        if (eachKey.equals("category") || eachKey.equals("xsd")) continue forKeys;
                        Attr attr =  doc.createAttribute(eachKey);
                        attr.setValue(elements.get(key).get(eachKey));
                        hijo.setAttributeNode(attr);

                    }

                    //llamada recursiva para generar todo el arbol
                    appendChildren(doc, hijo, key, mostrarID);
                }
            }
        }

        return ;
    }
	
	public String validateApp(String xml) {
		
		System.out.println("Asking for validating...");
		String result = null;
		try {
			result = validate("appValidation", xml);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return "ERROR: The application could not be validated.";
		}
		
		System.out.println("Validation: "+result);
		
		return result;
	}
	
	
	
	//////////////////////////////
	// Save methods
	//////////////////////////////
	private void saveSystemOnXML() throws Exception {
		
		DocumentBuilderFactory docFactory = DocumentBuilderFactory.newInstance();
        DocumentBuilder docBuilder = docFactory.newDocumentBuilder();
        Document doc = docBuilder.newDocument();
        
        
        // Genero elememto raiz del DOM
        Element rootElement = doc.createElement("system");
        doc.appendChild(rootElement);

        // 1. Save systemElements
        // ----------------------
        for (String element: systemElements.keySet()) {

        	// Genero elememto raiz del DOM
            Element xmlElement = doc.createElement("element");
            rootElement.appendChild(xmlElement);
            
            Attr attr = null;

            // Añado atributos al elemento
            attr =  doc.createAttribute("ID");
            attr.setValue(element);
            xmlElement.setAttributeNode(attr);
            
            for (String key : systemElements.get(element).keySet()) {
                attr =  doc.createAttribute(key);
                attr.setValue(systemElements.get(element).get(key));
                xmlElement.setAttributeNode(attr);
            }

        }
        
        // 2. Save applications
        // ----------------------
        for (String app: systemApps.keySet()) {
        	
        	// Genero elememto raiz del DOM
            Element xmlElement = doc.createElement("application");
            rootElement.appendChild(xmlElement);
            
            Attr attr = null;

            // Añado atributos a la aplicacion
            attr =  doc.createAttribute("ID");
            attr.setValue(app);
            xmlElement.setAttributeNode(attr);         
            
            for (String key : systemApps.get(app).keySet()) {
            	Element list = doc.createElement(key);
                xmlElement.appendChild(list);
                String elemName = key.substring(0, key.length() - 1);
                
                for (String entry : systemApps.get(app).get(key)) {
                	
                	Element elem = doc.createElement(elemName);
                	elem.appendChild(doc.createTextNode(entry));
                	list.appendChild(elem);
				}
            }
        }
		
        TransformerFactory transformerFactory = TransformerFactory.newInstance();
        Transformer transformer = transformerFactory.newTransformer();
        DOMSource source = new DOMSource(doc);
        
//        String fileName = "C:\\Users\\839073\\eclipse-oxygen-workspace\\SystemModel\\SystemModel.xml";
        String fileName = volumePath + "SystemModel.xml";
        File xmlFile = new File(fileName);
        FileWriter writer = new FileWriter(xmlFile);
        StreamResult result = new StreamResult(writer);
        
        xmlFile.setReadable(true, false);
        xmlFile.setWritable(true, false);
        
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "4");
        transformer.transform(source, result);
	}
	
	//////////////////////////////
	// Start methods
	//////////////////////////////
	public String appStart(String applicationID) {
		String result = "OK";
		
		
		System.out.println("Asking for start " + applicationID + " application");
		
		System.out.println(systemApps.get(applicationID));
		
		HashMap<String, String> componentImages = new HashMap<>();
		
		for (String componentID : systemApps.get(applicationID).get("components")) {
			
			// Por cada componente, crearemos su Dockerfile
			String dockerfile = createDockerfile(componentID);
			System.out.println("\nDockerfile:\n" + dockerfile);
			
			// TODO Quitar comentario
//			result = ComponentCreator.getInstance().buildComponent(applicationID, componentID, dockerfile);
			
			// TODO Borrar
			result = "OK";
			if (componentID.equals("sink_exist1"))
				result = "gcr.io/clusterekaitz/application1:sink_exist1";
			else if (componentID.equals("mqtt_source_http1"))
				result = "gcr.io/clusterekaitz/application1:mqtt_source_http1";
			// Fin borrar
			
			
			if (result.contains("ERROR")) {
				for (String toDelete : componentImages.values()) {
					ComponentCreator.getInstance().deleteComponent(toDelete);
				}
				return "ERROR: Component " + componentID + " could not be started. Message: " + result;
			} else
				componentImages.put(componentID, result);
		}
		
		// Guardaremos el nombre de la imagen de cada componente
		for (Entry<String, String> entry : componentImages.entrySet()) {
			System.out.println(entry.getKey() + " - " + entry.getValue());
			elements.get(entry.getKey()).put("image", entry.getValue());
			systemElements.get(entry.getKey()).put("image", entry.getValue());
		}
		
		try {
			saveSystemOnXML();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		// Una vez creada la aplicacion, se va a desplegar
		String deployResult = appDeploy(applicationID);
		
		return deployResult;
	}
	
	
	//////////////////////////////
	// Deploy methods
	//////////////////////////////
	public String appDeploy(String applicationID) {
		
		// Aqui hay que crear el docker-compose y enviarselo al Event Manager
		
		// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		// CUIDADO ! No hay que olvidarse de añadir la variable de entorno del OUTPUT a la hora de crear el docker-compose (para saber a quien es el siguiente componente)
		// Se lo podremos añadir en el docker-compose, asi le pondremos la variable OUTPUT y el nombre del siguiente elemento tendran el mismo valor
		
		String dockerComposeDef = createDockerCompose(applicationID);
		
		File folder = K8sManager.createYAMLFiles(dockerComposeDef, applicationID);
		if (folder == null)
			return "ERROR: YAML files could not be created.";
		
		try {
			K8sManager.deploy(folder);
		} catch (IOException | ApiException e) {
			e.printStackTrace();
			return "ERROR: YAML files could not be deployed in the cluster.";
		}
		
		
		return "done";
	}
	
	
	//////////////////////////////
	// Others methods
	//////////////////////////////
	public Hashtable<String, String> processAttribs(int firstAttribPos, String... cmdLine){

        if (cmdLine.length < 3) return null; //no hay atributos

        Hashtable<String, String> attribs = new Hashtable<String, String>();
        String attrib = "attrib";

        for (int i = firstAttribPos; i < cmdLine.length; i++) {
            if (cmdLine[i].contains("=")) { // encuentro otro atributo
                String[] attribDef = cmdLine[i].split("=");
                attrib = attribDef[0];

                attribs.put(attrib, (attribDef.length>1)?attribDef[1]:""); // puede estar vacío
            } else attribs.put(attrib, attribs.get(attrib) + " " + cmdLine[i]);
            String attribValue = attribs.get(attrib);
            while (attribValue.contains("{")) attribValue = attribValue.replace("{", "(");
            while (attribValue.contains("}")) attribValue = attribValue.replace("}", ")");
            while (attribValue.contains("#")) attribValue = attribValue.replace("#", "=");
            attribs.put(attrib, attribValue);

        }
        return attribs;
    }
	
	public String deleteElement(String ID) {
		return del(ID);
	}
	
	private String del(String prm) {
		
        String response = "not found";
        if (prm.equals("*")) {
            response = elements.size() + " deleted";
            elements.clear();

        } else if (elements.get(prm) != null) {
            elements.remove(prm);

            response = "done";
        }
        return response;
    }
	
	public String list(String... prm) {
		
		
		StringBuffer response = new StringBuffer("");
		if (prm[0].equals(("components"))) { // list components
            String comienzo = (prm.length>1 && !prm[1].isEmpty())? prm[1].replace("*", ".*"):"system.*";
            for (String key : elements.keySet()) {
                if (key.matches(comienzo)) {
                    response.append("\n\n").append(list(key)).append("\n");
                    response.append(getChildren(key, "\t"));
                }
            }
		} else if (prm[0].equals(("events"))) { // list events
			for (String element: elements.keySet()) {
	            if (element.matches(prm[0])) {
	                response.append("ID=" + element + " ");
	                elements: for (String key : elements.get(element).keySet()) {
//	                    if (key.equals("seParent")) continue elements;
//	                    if (key.equals("xsd")) { response.append("xsd=file "); continue elements;}
	                    response.append(key).append("=").append(elements.get(element).get(key)).append(" ");
	                }
	                response.append("\n");
	            }
	        }
        } else if  (prm[0].equals(("systemElements"))) { // list system elements
        	for (Entry<String, Hashtable<String, String>> entry : systemElements.entrySet()) {
        		response.append("ID=" + entry.getKey() + " category=" + entry.getValue().get("category") + "\n\t");
        		if (entry.getValue().get("category").equals("component")) {
	        		response.append("name=" + entry.getValue().get("name") + "\n");
	        		response.append("\ttype=" + entry.getValue().get("type") + "\n");
	        		response.append("\tfunction=" + entry.getValue().get("function"));
	        		
	        		if (entry.getValue().containsKey("inPort")) {
	        			response.append("\n\tinPort=" + entry.getValue().get("inPort"));
	        			response.append("\n\t\tdata=" + entry.getValue().get("dataIn"));
	        		}
	        		if (entry.getValue().containsKey("outPort")) {
	        			response.append("\n\toutPort=" + entry.getValue().get("outPort"));
	        			response.append("\n\t\tdata=" + entry.getValue().get("dataOut"));
	        		}
	        		
	        		response.append("\n");
        		}  else if (entry.getValue().get("category").equals("channel")) {
        			
    				response.append("from=" + entry.getValue().get("from") + "\n");
    				response.append("\t\tport=" + entry.getValue().get("fromPort") + "\n");
    				
    				response.append("\tto=" + entry.getValue().get("to") + "\n");
    				response.append("\t\tport=" + entry.getValue().get("toPort") + "\n");
    				
    				response.append("\tlink=" + entry.getValue().get("link") + "\n");
    				
        		} else if (entry.getValue().get("category").equals("event")) {
        			for (Entry<String, String> attribute : entry.getValue().entrySet()) {
	        			if ((attribute.getKey().equals("name")) || (attribute.getKey().equals("type")))
	        				response.append(attribute.getKey() + "=" + attribute.getValue() + " ");
					}
        			response.append("\n");
        		}
    		}
        } else {
        	for (Entry<String, Hashtable<String, String>> entry : elements.entrySet()) {
        		response.append("ID=" + entry.getKey() + " category=" + entry.getValue().get("category") + "\n\t");
        		if (entry.getValue().get("category").equals("component")) {
	        		response.append("name=" + entry.getValue().get("name") + "\n");
	        		response.append("\ttype=" + entry.getValue().get("type") + "\n");
	        		response.append("\tfunction=" + entry.getValue().get("function"));
	        		
	        		if (entry.getValue().containsKey("inPort")) {
	        			response.append("\n\tinPort=" + entry.getValue().get("inPort"));
	        			response.append("\n\t\tdata=" + entry.getValue().get("dataIn"));
	        		}
	        		if (entry.getValue().containsKey("outPort")) {
	        			response.append("\n\toutPort=" + entry.getValue().get("outPort"));
	        			response.append("\n\t\tdata=" + entry.getValue().get("dataOut"));
	        		}
	        		if (entry.getValue().containsKey("image"))
	        			response.append("\n\timage=" + entry.getValue().get("image"));
	        		
	        		response.append("\n");
        		}  else if (entry.getValue().get("category").equals("channel")) {
        			
    				response.append("from=" + entry.getValue().get("from") + "\n");
    				response.append("\t\tport=" + entry.getValue().get("fromPort") + "\n");
    				
    				response.append("\tto=" + entry.getValue().get("to") + "\n");
    				response.append("\t\tport=" + entry.getValue().get("toPort") + "\n");
    				
    				response.append("\tlink=" + entry.getValue().get("link") + "\n");
    				
        		} else if (entry.getValue().get("category").equals("event")) {
        			for (Entry<String, String> attribute : entry.getValue().entrySet()) {
	        			if ((attribute.getKey().equals("name")) || (attribute.getKey().equals("type")))
	        				response.append(attribute.getKey() + "=" + attribute.getValue() + " ");
					}
        			response.append("\n");
        		}
    		}
        	for (Entry<String, Hashtable<String, ArrayList<String>>> entryApps : systemApps.entrySet()) {
        		response.append("ID=" + entryApps.getKey() + "\n");
        		for (Entry<String, ArrayList<String>> attribute : entryApps.getValue().entrySet()) {
        			response.append("\t" + attribute.getKey() + "=" + attribute.getValue() + "\n");
				}
        	}
        	response.append("\n");
        }
		
		return response.toString();
	}
	
	private String getChildren(String parent, String prefijo) {
        StringBuffer response = new StringBuffer();
        for (String key : elements.keySet()) {
            for (String key2 : elements.get(key).keySet()) {
                if (key2.equals("parent") && elements.get(key).get(key2).equals(parent)) {
                    response.append(prefijo + list(key)).append("\n");
                    response.append(getChildren(key, prefijo + "\t"));
                } else if (key2.equals("node") && elements.get(key).get(key2).equals(parent)) {
                    response.append(prefijo + list(key)).append("\n");
                    response.append(getChildren(key, prefijo + "\t"));
                }
            }
        }
        return response.toString();
	
	}

	public String showSystem() throws Exception {
		
		//Build DOM
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true); // never forget this!
        DocumentBuilder builder = null;
        try {
            builder = factory.newDocumentBuilder();
        } catch (ParserConfigurationException e) {
            e.printStackTrace();
        }
        Document doc = null;
//        doc = builder.parse(new File("C:\\Users\\839073\\eclipse-oxygen-workspace\\SystemModel\\SystemModel.xml"));
        doc = builder.parse(new File(volumePath + "SystemModel.xml"));
		
        TransformerFactory transformerFactory = TransformerFactory.newInstance();
        Transformer transformer = transformerFactory.newTransformer();
        DOMSource source = new DOMSource(doc);
        StringWriter writer = new StringWriter();
        
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "4");
        transformer.transform(source, new StreamResult(writer));
        
        return writer.getBuffer().toString();
	}	
	
	private String createDockerfile(String componentID) {
		
		
		String baseImage = typeOfComponents.get(systemElements.get(componentID).get("type")).get("dockerfile").get("FROM");
		String cmd = typeOfComponents.get(systemElements.get(componentID).get("type")).get("dockerfile").get("CMD");
		String dockerfile = "FROM " +baseImage+ "\r\n" + 
				"\r\n" + 
				"ENV FUNCTION=" +systemElements.get(componentID).get("function")+ "\r\n" + 
				"\r\n";
		
		
		if (systemElements.get(componentID).containsKey("outPort"))
			dockerfile += "ENV outPort=" +systemElements.get(componentID).get("outPort")+ "\r\n" + 
					"\r\n";
		if (systemElements.get(componentID).containsKey("inPort"))
			dockerfile += "ENV inPort=" +systemElements.get(componentID).get("inPort")+ "\r\n" + 
					"\r\n";
		
		StringBuilder sb = new StringBuilder();
		String[] argms = cmd.split(" ");
		sb.append("[");
		for (String arg : argms) {
			sb.append("\"" + arg + "\", ");
		}
		sb.setLength(sb.length()-2);
		sb.append("]");
		
		dockerfile += "CMD " + sb.toString();
		
		return dockerfile;
		
	}
	
	public String createDockerCompose(String applicationID) {
		
		Map<String, Object> composeMap = new HashMap<>();
		composeMap.put("version", "2");
		Map<String, Object> services = new HashMap<>();
		
//		String previousComponent = null;
		for (String componentID : systemApps.get(applicationID).get("components")) {
			Map<String, Object> component = new HashMap<>();
			
			//String baseImage = typeOfComponents.get(systemElements.get(componentID).get("type")).get("dockerfile").get("FROM");
			String image = systemElements.get(componentID).get("image");
			
			String componentName = systemElements.get(componentID).get("name");
			component.put("image", image);
			component.put("container_name", componentName);
			
//			if (previousComponent != null) {
//				
//				// Añadimos un puerto al componente (para que se cree un services.yaml en el Event Manager)
//				List<Object> ports = new ArrayList<>();
//				ports.add("6000:6000");
//				component.put("ports", ports);
//			}
//			
			services.put(componentName, component);
//			previousComponent = componentName;
			
		}
		
		for (String channelID : systemApps.get(applicationID).get("channels")) {
			String fromComponentName = systemElements.get(systemElements.get(channelID).get("from")).get("name");
			String toComponentName = systemElements.get(systemElements.get(channelID).get("to")).get("name");
			
			// Añadimos la salida al siguiente componente
			Map<String, Object> fromComponent = (Map<String, Object>) services.get(fromComponentName);
			List<Object> envs = new ArrayList<>();
			envs.add("OUTPUT=" + toComponentName);
			fromComponent.put("environment", envs);
			services.put(fromComponentName, fromComponent);
			
			// Añadimos un puerto al componente (para que se cree un services.yaml en el Event Manager)
			Map<String, Object> toComponent = (Map<String, Object>) services.get(toComponentName);
			List<Object> ports = new ArrayList<>();
			ports.add("6000:6000");
			toComponent.put("ports", ports);
			services.put(toComponentName, toComponent);
			
			
		}
		
		composeMap.put("services", services);
		
		StringWriter sw = new StringWriter();
		Yaml yaml = new Yaml();
		yaml.dump(composeMap, sw);
		
		System.out.println(sw.toString());
		
		return sw.toString();
	}
	
	
	
	
	
}
