package utilities;

import elements.Planner;

public class Pruebas {
	
	public static void main(String[] args) throws Exception {
		String xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\r\n" + 
				"<application xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"/xmlSchemas/Application.xsd\" name=\"data_adquisition\">\r\n" + 
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
		
        
		Planner p = Planner.getInstance();
		
		String ID = p.appRegister(xml);
		
		if (ID == null)
			System.out.println("--> App not registered.");
		else
			System.out.println("Application ID --> " + ID);
		
//		System.out.println("\n--------------------\n" + SystemModel.getInstance().list(""));
//		System.out.println("\n--------------------\n" + SystemModel.getInstance().list("systemElements"));
		
		
//		System.out.println(SystemModel.getInstance().showSystem());
		
	}

}
