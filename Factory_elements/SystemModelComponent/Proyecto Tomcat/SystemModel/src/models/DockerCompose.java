package models;

import java.util.Map;

public class DockerCompose {
	
	private String version;
	private Map<String, Component> services;
	
	
	public String getVersion() {
		return version;
	}
	
	public Map<String, Component> getServices() {
		return services;
	}


	public void setVersion(String version) {
		this.version = version;
	}
	
	public void setServices(Map<String, Component> services) {
		this.services = services;
	}
	
	
	@Override
	public String toString() {
		return "DockerCompose [version=" + version + ", services=" + services + "]";
	}
	
	

}



