package utilities;

import java.io.File;
import java.io.PrintWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.Source;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.w3c.dom.Document;
import org.xml.sax.InputSource;

import components.Planner;
import components.SystemModel;

public class Pruebas {
	
	public static void main(String[] args) throws Exception {
		
		String xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\r\n" + 
				"<application xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" name=\"data_adquisition\">\r\n" + 
				"  <componentInstance name=\"get_data_from_plant\" type=\"MQTT_SOURCE_HTTP\" description=\"component instance description\">\r\n" + 
				"    <function name=\"assemblyStationData\" description=\"description of function\"/>\r\n" + 
				"    <outPort name=\"TStation\" id=\"get_data_from_plant::TStation\">\r\n" + 
				"      <data name=\"product\" type=\"TPlant\"/>\r\n" + 
				"    </outPort>\r\n" + 
				"  </componentInstance>\r\n" + 
				"  <componentInstance name=\"sink_exist_plant_data\" type=\"SINK_EXIST\" description=\"component instance description\">\r\n" + 
				"    <function name=\"storeAssemblyStationData\" description=\"description of function\"/>\r\n" + 
				"    <inPort name=\"TStation\" id=\"sink_exist_plant_data::TStation\">\r\n" + 
				"      <data name=\"product\" type=\"TPlant\"/>\r\n" + 
				"    </inPort>\r\n" + 
				"  </componentInstance>\r\n" + 
				"  <channel from=\"get_data_from_plant::TStation\" link=\"http\" to=\"sink_exist_plant_data::TStation\"/>\r\n" + 
				"</application>";
		
        
//		Planner p = Planner.getInstance();
//		
//		String ID = p.appRegister(xml);
//		
//		if (ID == null)
//			System.out.println("--> App not registered.");
//		else
//			System.out.println("Application ID --> " + ID);
//		
//		System.out.println("\n--------------------\n" + SystemModel.getInstance().list(""));
//		System.out.println("\n--------------------\n" + SystemModel.getInstance().list("systemElements"));
//		
//		System.out.println("Validating all application...");
//		
//		String xml2 = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\r\n" + 
//				"<application xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"/xmlSchemas/Application.xsd\" name=\"data_adquisition\">\r\n" + 
//				"  <componentInstance name=\"get_data_from_plant\" type=\"MQTT_SOURCE_HTTP\" description=\"component instance description\">\r\n" + 
//				"    <function name=\"assemblyStationData\" description=\"description of function\"/>\r\n" + 
//				"    <outPort name=\"TStation\" id=\"get_data_from_plant::TStation\">\r\n" + 
//				"      <data name=\"product\" type=\"TPlant\"/>\r\n" + 
//				"    </outPort>\r\n" + 
//				"  </componentInstance>\r\n" + 
//				"  <componentInstance name=\"sink_exist_plant_data\" type=\"SINK_EXIST\" description=\"component instance description\">\r\n" + 
//				"    <function name=\"storeAssemblyStationData\" description=\"description of function\"/>\r\n" + 
//				"    <inPort name=\"TStation\" id=\"sink_exist_plant_data::TStation\">\r\n" + 
//				"      <data name=\"product\" type=\"TPlant\"/>\r\n" + 
//				"    </inPort>\r\n" + 
//				"  </componentInstance>\r\n" + 
//				"  <channel from=\"get_data_from_plant::TStation\" link=\"http\" to=\"sink_exist_plant_data::TStation\"/>\r\n" + 
//				"</application>";
//		
//		SystemModel.getInstance().validateApp(xml2);
		
		
//		System.out.println(SystemModel.getInstance().showSystem());
		
		
		
		String cmd = "python3 subs.py";
		System.out.println(cmd);
		
		StringBuilder sb = new StringBuilder();
		String[] argms = cmd.split(" ");
		sb.append("[");
		for (String arg : argms) {
			sb.append("\"" + arg + "\", ");
		}
		sb.setLength(sb.length()-2);
		sb.append("]");
		System.out.println("CMD " + sb.toString());
		System.out.println("CMD [\"catalina.sh\", \"run\"]");
		
		
//		File f = new File ("C:\\Users\\839073\\eclipse-oxygen-workspace\\aa.txt");
//		System.out.println(f.getAbsolutePath());
//		
//		String a = null;
//		if (a.contains("aa"))
//			System.out.println("da");
		
//		SystemModel.getInstance().createDockerCompose(null);
		
		String dockerfile = "FROM gcr.io/clusterekaitz/sink:exist\r\n" + 
				"\r\n" + 
				"ENV FUNCTION=storeAssemblyStationData\r\n" + 
				"\r\n" + 
				"ENV inPort=TStation\r\n" + 
				"\r\n" + 
				"CMD [\"catalina.sh\", \"run\"]";
		
		
//		String result = ComponentCreator.getInstance().buildComponent("application1", "sink-exist", dockerfile);
		
		
		//////////////////////////////////////////////
		// PRUEBA para validacion aplicacion completa
		//////////////////////////////////////////////
		System.out.println("\nPrueba validacion completa.\n");
		
		
		//Parser that produces DOM object trees from XML content
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
         
        //API to obtain DOM Document instance
        DocumentBuilder builder = null;
        Document doc = null;
        try
        {
            //Create DocumentBuilder with default configuration
            builder = factory.newDocumentBuilder();
             
            //Parse the content to Document object
            doc = builder.parse(new InputSource(new StringReader(xml)));
        } 
        catch (Exception e) 
        {
            e.printStackTrace();
        }
        
        SchemaFactory schemaFactory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
    	
        byte[] encoded = Files.readAllBytes(Paths.get("C:\\Users\\839073\\Documents\\System Model Component\\Prueba Validacion completa\\Application.xsd"));
    	
    	Source schemaFile = new StreamSource(new StringReader(new String(encoded, StandardCharsets.UTF_8)));
        Schema schema = schemaFactory.newSchema(schemaFile);
        
         // create a Validator instance, which can be used to validate an instance document
        Validator validator = schema.newValidator();
        // validate the DOM tree
        try {
            validator.validate(new DOMSource(doc));
        } catch (Exception e) {
            StringWriter sw = new StringWriter();
            e.printStackTrace(new PrintWriter(sw));
            System.out.println("ERROR!!!");
            System.out.println(sw.toString());
        }
		
		System.out.println(xml);
		
		
	}

}
