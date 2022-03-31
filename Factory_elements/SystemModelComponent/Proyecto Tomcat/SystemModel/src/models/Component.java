package models;

import java.util.Hashtable;
import java.util.List;

public class Component {
	
	private int positionInFlow;
	private String baseImage;
	private Hashtable<String, String> envVariables;
	private String executionCommand;
	
	
	public Component(int positionInFlow, String baseImage, String executionCommand) {
		super();
		this.positionInFlow = positionInFlow;
		this.baseImage = baseImage;
		this.executionCommand = executionCommand;
		this.envVariables = new Hashtable<>();
	}
	
	public void addEnvVariable(String envName, String envValue) {
		this.envVariables.put(envName, envValue);
	}

	/* 
	 * GETTERS
	 */
	public int getPositionInFlow() {
		return positionInFlow;
	}
	
	public String getBaseImage() {
		return baseImage;
	}

	public Hashtable<String, String> getEnvVariables() {
		return envVariables;
	}
	
	public String getExecutionCommand() {
		return executionCommand;
	}
	
	
	/* 
	 * SETTERS
	 */
	public void setPositionInFlow(int positionInFlow) {
		this.positionInFlow = positionInFlow;
	}
	
	public void setBaseImage(String baseImage) {
		this.baseImage = baseImage;
	}

	public void setEnvVariables(Hashtable<String, String> envVariables) {
		this.envVariables = envVariables;
	}
	
	public void setExecutionCommand(String executionCommand) {
		this.executionCommand = executionCommand;
	}

	@Override
	public String toString() {
		return "Component [positionInFlow=" + positionInFlow + ", baseImage=" + baseImage + ", envVariables="
				+ envVariables + ", executionCommand=" + executionCommand + "]";
	}

	public String getEnvVariable(String name) {
		return this.envVariables.get(name);
	}

	
	
	
	
}
