package appfil1;

import functions.StoreAssemblyStationData;

public class Sink_eXist {
	
public static void main(String[] args) {
		
		Thread t_storeAssemblyStationData = new StoreAssemblyStationData();
		
//		String function = System.getenv("FUNCTION");
		String function = "storeAssemblyStationData";
		
		if (function.equals("storeAssemblyStationData"))
			t_storeAssemblyStationData.start();
//			getAssemblyStationData();
		
		
	}

}
