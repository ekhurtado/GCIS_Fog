package components;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;

import org.yaml.snakeyaml.Yaml;

import io.kubernetes.client.ApiClient;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.Configuration;
import io.kubernetes.client.apis.AppsV1Api;
import io.kubernetes.client.apis.CoreV1Api;
import io.kubernetes.client.custom.IntOrString;
import io.kubernetes.client.models.V1Deployment;
import io.kubernetes.client.models.V1Service;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.KubeConfig;

public class EventManager {
	
	// Singleton pattern
    private static EventManager instance = new EventManager();
    
    
    private EventManager() {

    }

    public static EventManager getInstance() {
        return instance;
    }
    
    
    
	//////////////////////////////
	// Deploy methods
	//////////////////////////////
	
	public String appDeploy(String dockerComposeDef, String applicationID) {
		System.out.println(dockerComposeDef);
		
		// Creating a folder to the application
		File folder = new File("/event_manager/" + applicationID);
		folder.mkdir();
		folder.setReadable(true, false);
		folder.setWritable(true, false);
		
		// Creating Docker Compose file
		BufferedWriter bufferedWriter;
		try {
			bufferedWriter = new BufferedWriter(new FileWriter("/event_manager/" +applicationID+ "/docker-compose.yml"));
			bufferedWriter.write(dockerComposeDef);
			bufferedWriter.close();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		// Crear los archivos de despliegue para Kubernetes
		try {
			System.out.println("\n Executing kompose command...\n");
			execCommand("kompose convert -f /event_manager/docker-compose.yml -o /event_manager/");
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		// Desplegarlos en Kubernetes
		try {
			deploy(folder);
		} catch (IOException | ApiException e) {
			
			e.printStackTrace();
		}
		
		return "done";
	}
	

	private void execCommand(String command) throws IOException {
		
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
    
	
	private void deploy(File folder) throws IOException, ApiException {
		
		System.out.println("Deploying application on Kubernetes...");

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
	

}
