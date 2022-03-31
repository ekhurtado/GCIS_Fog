package models;

import java.util.ArrayList;

public class Event {

	private String eventName;
	private ArrayList<String> actions;
	
	
	public Event(String eventName) {
		super();
		this.eventName = eventName;
		this.actions = new ArrayList<>();
	}


	public String getEventName() {
		return eventName;
	}


	public void setEventName(String eventName) {
		this.eventName = eventName;
	}


	public ArrayList<String> getActions() {
		return actions;
	}


	public void setActions(ArrayList<String> actions) {
		this.actions = actions;
	}
	
	
	
}
