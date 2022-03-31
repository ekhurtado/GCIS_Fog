package utilities;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import java.util.ArrayList;

public class XMLReadElement {
	
    public static ArrayList<ArrayList<ArrayList<String>>> readElement (Document doc) {

    	
        
        ArrayList<ArrayList<ArrayList<String>>> xmlelements = new ArrayList<ArrayList<ArrayList<String>>>();
        
        // Primero vamos a añadir los datos de la aplicacion
        NodeList appList = doc.getElementsByTagName("application");
        Node appNode = appList.item(0);
        Element appElem = (Element) appNode;

        xmlelements.add(new ArrayList<>());
        xmlelements.get(0).add(new ArrayList<>());
        xmlelements.get(0).add(new ArrayList<>());
        xmlelements.get(0).add(new ArrayList<>());
        
        xmlelements.get(0).get(0).add(appNode.getNodeName());
        xmlelements.get(0).get(1).add("name");
        xmlelements.get(0).get(2).add(appElem.getAttribute("name"));
        
        
        int pos = 1;
        // Despues vamos a añadir los datos de los componentes
        NodeList componentList = doc.getElementsByTagName("componentInstance");
		for (int i = 0; i < componentList.getLength(); i++) {
			Node compNode = componentList.item(i);
			Element compElem = (Element) compNode;
			
			xmlelements.add(new ArrayList<>());
			xmlelements.get(pos).add(new ArrayList<>());
			xmlelements.get(pos).add(new ArrayList<>());	// Attribute names' list
			xmlelements.get(pos).add(new ArrayList<>());	// Attribute values' list
			
			xmlelements.get(pos).get(0).add("componentInstance");
			xmlelements.get(pos).get(1).add("name");
			xmlelements.get(pos).get(2).add(compElem.getAttribute("name"));
			xmlelements.get(pos).get(1).add("type");
			xmlelements.get(pos).get(2).add(compElem.getAttribute("type"));
			
			NodeList functionList = compElem.getElementsByTagName("function");
			Element functionElem = (Element) functionList.item(0);
			xmlelements.get(pos).get(1).add("function");
			xmlelements.get(pos).get(2).add(functionElem.getAttribute("name"));
			
			
			if (compElem.getElementsByTagName("outPort").item(0) != null) {
				NodeList outPortList = compElem.getElementsByTagName("outPort");
				Element outPortElem = (Element) outPortList.item(0);
				xmlelements.get(pos).get(1).add("outPort");
				xmlelements.get(pos).get(2).add(outPortElem.getAttribute("name"));
				
				NodeList dataList = outPortElem.getElementsByTagName("data");
				Element dataElem = (Element) dataList.item(0);
				xmlelements.get(pos).get(1).add("dataOut");
				xmlelements.get(pos).get(2).add(dataElem.getAttribute("type"));
			}
			
			if (compElem.getElementsByTagName("inPort").item(0) != null) {
				NodeList inPortList = compElem.getElementsByTagName("inPort");
				Element inPortElem = (Element) inPortList.item(0);
				xmlelements.get(pos).get(1).add("inPort");
				xmlelements.get(pos).get(2).add(inPortElem.getAttribute("name"));
				
				NodeList dataList = inPortElem.getElementsByTagName("data");
				Element dataElem = (Element) dataList.item(0);
				xmlelements.get(pos).get(1).add("dataIn");
				xmlelements.get(pos).get(2).add(dataElem.getAttribute("type"));
				
			}
			
			pos ++;
		}
		
		// Por ultimo, añadiremos los datos de los canales
		NodeList channelList = doc.getElementsByTagName("channel");
		for (int i = 0; i < channelList.getLength(); i++) {
			Node channelNode = channelList.item(i);
			Element channelElem = (Element) channelNode;
			
			xmlelements.add(new ArrayList<>());
			xmlelements.get(pos).add(new ArrayList<>());
			xmlelements.get(pos).add(new ArrayList<>());	// Attribute names' list
			xmlelements.get(pos).add(new ArrayList<>());	// Attribute values' list
			
			xmlelements.get(pos).get(0).add("channel");
			xmlelements.get(pos).get(1).add("from");
			xmlelements.get(pos).get(2).add(channelElem.getAttribute("from"));
			xmlelements.get(pos).get(1).add("to");
			xmlelements.get(pos).get(2).add(channelElem.getAttribute("to"));
			xmlelements.get(pos).get(1).add("link");
			xmlelements.get(pos).get(2).add(channelElem.getAttribute("link"));
			
			pos ++;
		}
		
        return xmlelements;
    }
}
