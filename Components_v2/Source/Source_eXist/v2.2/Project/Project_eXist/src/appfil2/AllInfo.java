package appfil2;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

public class AllInfo {
	
	private String machineID;
	private HashMap<String, String> plannedTimes = new HashMap<>();	// HashMap with all actionsID and the planned start and finish time --> <actionID>=<plannedStartTime>&<plannedFinishTime> (2=09:10:00&09:10:45)
	private HashMap<String, String> actualTimes = new HashMap<>();	// HashMap with all actionsID and the actual start and finish time --> <actionID>=<actualStartTime>&<actualFinishTime> (2=09:10:20&09:11:00)
	
	
	
	public AllInfo(String machineID) {
		this.machineID = machineID;
		this.plannedTimes = new HashMap<>();
		this.actualTimes = new HashMap<>();
	}

	//////////////////////////////////////////////////////
	// Methods to add information to machine data
	//////////////////////////////////////////////////////
	
	public void addNewPlannedTime(String actionID, String plannedTime) {
		// Location format: <plannedStartTime>&<plannedFinishTime>
		if (!this.plannedTimes.containsKey(actionID))
			this.plannedTimes.put(actionID, plannedTime);
	}
	
	public void addNewActualTime(String actionID, String actualTime) {
		// Location format: <plannedStartTime>&<plannedFinishTime>
		if (!this.actualTimes.containsKey(actionID))
			this.actualTimes.put(actionID, actualTime);
	}
	
	
	//////////////////////////////////////////////////////
	// Get methods
	//////////////////////////////////////////////////////
	public String getMachineID() {
		return machineID;
	}

	public HashMap<String, String> getPlannedTimes() {
		return plannedTimes;
	}

	public HashMap<String, String> getActualTimes() {
		return actualTimes;
	}

	// toString methods
	
	@Override
	public String toString() {
		return "AllInfo [machineID=" + machineID + ", plannedTimes=" + plannedTimes
				+ ", actualTimes=" + actualTimes + "]";
	}

	public String actualTimesToString() {
		StringBuilder sb = new StringBuilder();
		sb.append("[");
		
		Iterator it = actualTimes.entrySet().iterator();
	    while (it.hasNext()) {
	        Map.Entry pair = (Map.Entry)it.next();
	        sb.append("\n{" + pair.getKey() + ": " + pair.getValue() + "},\n");
	    }
	    if (!actualTimes.isEmpty()) {
		    sb.delete(sb.length()-2, sb.length());
		    sb.deleteCharAt(1);
	    }
	    sb.append("]\n");
		
		return sb.toString();
		
	}

	public String plannedTimesToString() {
		StringBuilder sb = new StringBuilder();
		sb.append("[");
		
		Iterator it = plannedTimes.entrySet().iterator();
	    while (it.hasNext()) {
	        Map.Entry pair = (Map.Entry)it.next();
	        sb.append("\n{" + pair.getKey() + ": " + pair.getValue() + "},\n");
	    }
	    if (!plannedTimes.isEmpty()) {
		    sb.delete(sb.length()-2, sb.length());
		    sb.deleteCharAt(1);
	    }
	    sb.append("]\n");
		
		return sb.toString();
	}

	public void updateActualAction(String itemID, String actionID, String hashMapKey) {
		String time = this.actualTimes.remove(hashMapKey);
		this.actualTimes.put(itemID + ":" + hashMapKey.split(":")[1] + "," + actionID, time);
	}
		
	public void updatePlannedAction(String itemID, String actionID, String hashMapKey) {
		String time = this.plannedTimes.remove(hashMapKey);
		this.plannedTimes.put(itemID + ":" + hashMapKey.split(":")[1] + "," + actionID, time);
		
	}

	public JSONObject getJSON() {
		JSONObject json = new JSONObject();
		json.put("machineID", machineID);
		// Actual times
		JSONArray actualArray = getJSONArray(actualTimes);
	    json.put("actualTimes", actualArray);
	    
	    // Planned times
	    JSONArray plannedArray = getJSONArray(plannedTimes);
	    json.put("plannedTimes", plannedArray);
	    
		
		return json;
	}

	private JSONArray getJSONArray(HashMap<String, String> hashmap) {
		Iterator it = hashmap.entrySet().iterator();
		JSONArray actualArray = new JSONArray();
		JSONObject jsonObject;
	    while (it.hasNext()) {
	        Map.Entry pair = (Map.Entry)it.next();
	        jsonObject = new JSONObject();
	        
	        String key = (String) pair.getKey();
	        jsonObject.put("Item", key.split(":")[0]);
	        jsonObject.put("Action", key.split(":")[1]);

	        if (pair.getValue() != "") {
		        String value = (String) pair.getValue();
		        jsonObject.put("Start", value.split("&")[0]);
		        jsonObject.put("Finish", value.split("&")[1]);
	        } else {
	        	jsonObject.put("Start", null);
		        jsonObject.put("Finish", null);
	        }
	        
	        actualArray.add(jsonObject);
	    }
	    
	    return actualArray;
	}

	
	
	
}
