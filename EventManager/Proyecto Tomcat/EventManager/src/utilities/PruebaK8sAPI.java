package utilities;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.yaml.snakeyaml.Yaml;

import com.squareup.okhttp.Call;

import components.EventManager;
import io.kubernetes.client.ApiClient;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.Configuration;
import io.kubernetes.client.apis.AppsV1Api;
import io.kubernetes.client.apis.CoreV1Api;
import io.kubernetes.client.apis.ExtensionsV1beta1Api;
import io.kubernetes.client.custom.IntOrString;
import io.kubernetes.client.models.ExtensionsV1beta1Deployment;
import io.kubernetes.client.models.V1Container;
import io.kubernetes.client.models.V1Deployment;
import io.kubernetes.client.models.V1LoadBalancerStatus;
import io.kubernetes.client.models.V1Namespace;
import io.kubernetes.client.models.V1ObjectMeta;
import io.kubernetes.client.models.V1Service;
import io.kubernetes.client.models.V1ServiceBuilder;
import io.kubernetes.client.models.V1ServiceList;
import io.kubernetes.client.models.V1ServicePort;
import io.kubernetes.client.models.V1ServiceStatus;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.KubeConfig;

public class PruebaK8sAPI {
	
	public static void main(String[] args) throws IOException, ApiException {
		
		String dockerCompose = "services:\r\n" + 
				"  sink_exist_plant_data:\r\n" + 
				"    image: gcr.io/clusterekaitz/sink:exist\r\n" + 
				"    container_name: sink_exist_plant_data\r\n" + 
				"    ports: ['8080:8080']\r\n" + 
				"  get_data_from_plant:\r\n" + 
				"    image: gcr.io/clusterekaitz/source:mqtt-http\r\n" + 
				"    environment: [OUTPUT=sink_exist_plant_data]\r\n" + 
				"    container_name: get_data_from_plant\r\n" + 
				"version: '2'";
		
		
		deployApplication(dockerCompose);
		
		/*
		// TODO Pruebas
		
		// Kubernetes API
		String kubeConfigPath = ".kube/config";
		ApiClient client = ClientBuilder.kubeconfig(KubeConfig.loadKubeConfig(new FileReader(kubeConfigPath))).build();
		Configuration.setDefaultApiClient(client);

        AppsV1Api appsAPI = new AppsV1Api();
        CoreV1Api coreAPI = new CoreV1Api();

		String svcPath = "/event_manager/application1/sink-exist-plant-data-service.yaml";
		File file = new File(svcPath);
		
		Yaml yaml = new Yaml();
		FileReader fr = new FileReader(file);
	    FileInputStream input = new FileInputStream(file);
		Map map = (Map) yaml.load(input);
		
		V1Service svcBody = (V1Service) yaml.loadAs(fr, V1Service.class);
		System.out.println("\n Deploying new Service...");
		System.out.println("INFO:");
		System.out.println("-> " + svcBody);
		
		int targetPort = Integer.parseInt(svcBody.getSpec().getPorts().get(0).getTargetPort().getStrValue());
		svcBody.getSpec().getPorts().get(0).setTargetPort(new IntOrString(targetPort));
		
		V1Service newSvc = coreAPI.createNamespacedService("default", svcBody, null, null, null);
		System.out.println(" Deployed:  " + newSvc.getMetadata().getName());
		*/
		
		
	}
	
	

	private static void deployApplication(String dockerCompose)
			throws IOException, FileNotFoundException, ApiException {
		// Creamos la carpeta
		System.out.println("\n Creating main folder...\n");
		File folder = new File("/event_manager/application1");
		folder.mkdir();
		
		folder.setReadable(true, false);
		folder.setWritable(true, false);
		
		// Creamos el Docker Compose
		System.out.println("\n Creating docker-compose...\n");
		BufferedWriter bufferedWriter;
		try {
			bufferedWriter = new BufferedWriter(new FileWriter("/event_manager/application1/docker-compose.yml"));
			bufferedWriter.write(dockerCompose);
			bufferedWriter.close();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		// Creamos los YAML
		System.out.println("\n Executing kompose command...\n");
		execCommand("kompose convert -f /event_manager/application1/docker-compose.yml -o /event_manager/application1/");
		
		String folderPath = "/event_manager/application1";
		FileReader fr = null;
	    InputStream input = null;
	    Map map = null;
		Yaml yaml = new Yaml();
		
		// Kubernetes API
		String kubeConfigPath = ".kube/config";
		ApiClient client = ClientBuilder.kubeconfig(KubeConfig.loadKubeConfig(new FileReader(kubeConfigPath))).build();
		Configuration.setDefaultApiClient(client);
		
		System.out.println("Kubernetes API is ready.");

        AppsV1Api appsAPI = new AppsV1Api();
        CoreV1Api coreAPI = new CoreV1Api();
		
		System.out.println("\n Creating and deploying all YAML...\n");
        for (File file : folder.listFiles()) {
        	
        	file.setReadable(true, false);
    		file.setWritable(true, false);
        	
            if (file.getName().contains("docker-compose"))
            	continue;
            else {
            	fr =new FileReader(file);
        	    input = new FileInputStream(file);
        		map = (Map) yaml.load(input);
        		
        		if (map.get("kind").equals("Deployment")) {
        			V1Deployment deployBody = (V1Deployment) yaml.loadAs(fr, V1Deployment.class);
        			System.out.println("---" + deployBody.getKind());
        			System.out.println("---" + deployBody.getMetadata().getName());
        			
        			System.out.println("\n Deploying new Deployment...");
        			V1Deployment newDeploy = appsAPI.createNamespacedDeployment("default", deployBody, Boolean.FALSE, null, null);
        			System.out.println(" Deployed:  " + newDeploy.getMetadata().getName());
        			
        		} else if (map.get("kind").equals("Service")) {
        			V1Service svcBody = (V1Service) yaml.loadAs(fr, V1Service.class);
        			System.out.println("---" + svcBody.getKind());
        			System.out.println("---" + svcBody.getMetadata().getName());
        			
        			// Al convertir con Kompose se convierte mal el TargetPort: tiene que ser int, con String no funciona
        			int targetPort = Integer.parseInt(svcBody.getSpec().getPorts().get(0).getTargetPort().getStrValue());
        			svcBody.getSpec().getPorts().get(0).setTargetPort(new IntOrString(targetPort));
        			
        			
        			System.out.println("\n Deploying new Service...");
        			V1Service newSvc = coreAPI.createNamespacedService("default", svcBody, null, null, null);
        			System.out.println(" Deployed:  " + newSvc.getMetadata().getName());
        		}
        		
        		fr.close();
        		input.close();
            }
        }
	}
	
	private static void execCommand(String command) throws IOException {
		
		Process process = null;
		try {
			process = Runtime.getRuntime().exec(command);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		InputStream inputstream = process.getInputStream();
		BufferedInputStream bufferedinputstream = new BufferedInputStream(inputstream);
		
		byte[] contents = new byte[1024];

		int bytesRead = 0;
		String strFileContents = ""; 
		while((bytesRead = bufferedinputstream.read(contents)) != -1) { 
		    strFileContents += new String(contents, 0, bytesRead);              
		}
		
		inputstream.close();
		bufferedinputstream.close();

		System.out.print(strFileContents);
		
		
	}
	

	private static void removeAttribute(File file, String attributeName) {

		String currentLine;
		try {
			
			File tempFile = new File(file.getParent() + File.separator + "tempFile.yaml");
			
			// Le damos permisos porque al crear un nuevo archivo se crea sin ellos
			tempFile.setReadable(true, false);
	    	tempFile.setWritable(true, false);
	    	file.setReadable(true, false);
	    	file.setWritable(true, false);
			
			BufferedReader reader = new BufferedReader(new FileReader(file));
			BufferedWriter writer = new BufferedWriter(new FileWriter(tempFile));
			
			while((currentLine = reader.readLine()) != null) {
			    // trim newline when comparing with lineToRemove
			    String trimmedLine = currentLine.trim();
			    if(trimmedLine.contains(attributeName)) continue;
			    writer.write(currentLine + System.getProperty("line.separator"));
			}
			
			writer.close(); 
			reader.close();
			
			file.delete();
			tempFile.renameTo(file);
			
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}

}
