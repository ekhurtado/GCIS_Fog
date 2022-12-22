package appfil2;

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

import functions.GetAssemblyStationData;



public class Source_eXist {
	
	// SDE --> Source Datos Estaciones
	
    
	public static void main(String[] args) {
		
		Thread t_getAssemblyStationData = new GetAssemblyStationData();
		
		String function = System.getenv("FUNCTION");
//		String function = "getAssemblyStationData";
		
		if (function.equals("getAssemblyStationData"))
			t_getAssemblyStationData.start();
//			getAssemblyStationData();
		
		
	}
	
	

	

}
