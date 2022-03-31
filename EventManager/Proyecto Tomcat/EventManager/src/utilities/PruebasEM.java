package utilities;

import java.io.StringWriter;
import java.util.HashMap;
import java.util.Map;

import org.yaml.snakeyaml.Yaml;

public class PruebasEM {
	
	public static void main(String[] args) {
		
		String dockerCompose = "services:\r\n" + 
				"    sink_exist_plant_data: {image: 'gcr.io/clusterekaitz/sink:exist', container_name: sink_exist_plant_data}\r\n" + 
				"    get_data_from_plant:\r\n" + 
				"        image: gcr.io/clusterekaitz/source:mqtt-http\r\n" + 
				"        environment: [OUTPUT=sink_exist_plant_data]\r\n" + 
				"        container_name: get_data_from_plant\r\n" + 
				"        ports: ['6000:6000']\r\n" + 
				"version: '2'";
		
		String compose2 = "services:\\n  sink_exist_plant_data: {image: 'gcr.io/clusterekaitz/sink:exist', container_name: sink_exist_plant_data}\\n  get_data_from_plant:\\n    image: gcr.io/clusterekaitz/source:mqtt-http\\n    environment: [OUTPUT=sink_exist_plant_data]\\n    container_name: get_data_from_plant\\n    ports: ['6000:6000']\\nversion: '2'\\n";
		
		
		compose2 = compose2.replace("\\n", "\n");
		
		Yaml yaml = new Yaml();
		Map<String, Object> dockerComposeMap = yaml.load(compose2);

		StringWriter sw = new StringWriter();
		yaml.dump(dockerComposeMap, sw);
		
		System.out.println(sw.toString());
		
		
		// ---------------------------------------
		
		Map<String, Object> composeMap = new HashMap<>();
		composeMap.put("version", "2");
		Map<String, Object> services = new HashMap<>();
		
		Map<String, Object> component = new HashMap<>();
		component.put("aa", "bb");
		component.put("cc", "dd");
		component.put("dd", "ff");
		
		Map<String, Object> component2 = new HashMap<>();
		component2.put("aa", "bb");
		component2.put("cc", "dd");
		component2.put("dd", "ff");
		
		services.put("comp1", component);
		services.put("comp2", component2);
		
		composeMap.put("services", services);
		
		sw = new StringWriter();
		yaml = new Yaml();
		yaml.dump(composeMap, sw);
		System.out.println("Con HashMap:");
		
		String aa = sw.toString().replace("\n", "\\n");
		aa = aa.replace("\r", "\\r");
		
		System.out.println(aa);
		
		
		
		if (sw.toString().contains("\n"))
			System.out.println("Tiene");
		
	}

}
