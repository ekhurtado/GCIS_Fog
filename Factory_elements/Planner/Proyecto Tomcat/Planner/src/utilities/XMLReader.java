package utilities;

import java.io.IOException;
import java.io.StringReader;
import java.util.ArrayList;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

public class XMLReader {
	
	public static ArrayList<ArrayList<ArrayList<String>>> readFile (String xmlContent) {
		
        
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
        try {
            doc = builder.parse(new InputSource(new StringReader(xmlContent)));
        } catch (SAXException e) {
//            e.printStackTrace();
            return null;
        } catch (IOException e) {
//            e.printStackTrace();
            return null;
        }

        ArrayList<ArrayList<ArrayList<String>>> xmlelements = XMLReadElement.readElement(doc);
		
        return xmlelements;
	}

}
