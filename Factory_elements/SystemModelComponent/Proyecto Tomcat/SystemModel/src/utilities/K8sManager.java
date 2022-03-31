package utilities;

import java.io.BufferedInputStream;
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
import io.kubernetes.client.models.V1DeploymentList;
import io.kubernetes.client.models.V1Service;
import io.kubernetes.client.models.V1ServiceList;
import io.kubernetes.client.util.ClientBuilder;
import io.kubernetes.client.util.KubeConfig;

public class K8sManager {
	
	private static String volumePath = "/system_model/";

	
	///////////////////////////////////////////
	// METODOS TRAIDOS DESDE EL EVENT MANAGER
	///////////////////////////////////////////

	public static File createYAMLFiles(String dockerComposeDef, String applicationID) {
		System.out.println(dockerComposeDef);
		
		// Primero, nos aseguramos que existe la carpeta que contiene todas las definiciones de las aplicaciones
		File appsFolder = new File(volumePath + "applications");
		appsFolder.mkdir();
		appsFolder.setReadable(true, false);
		appsFolder.setWritable(true, false);
		
		
		// Creating a folder to the application
		File folder = new File(volumePath + "applications/" + applicationID);
		folder.mkdir();
		folder.setReadable(true, false);
		folder.setWritable(true, false);
		
		// Creating Docker Compose file
		BufferedWriter bufferedWriter;
		try {
			bufferedWriter = new BufferedWriter(new FileWriter(volumePath + "applications/" +applicationID+ "/docker-compose.yml"));
			bufferedWriter.write(dockerComposeDef);
			bufferedWriter.close();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		// Crear los archivos de despliegue para Kubernetes
		try {
			System.out.println("\nExecuting kompose command...\n");
			execCommand("kompose convert -f " + volumePath + "applications/" + applicationID + "/docker-compose.yml -o " + volumePath + "applications/" + applicationID);
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	
		// Desplegarlos en Kubernetes
		//try {
		//	deploy(folder);
		//} catch (IOException | ApiException e) {
		//
		//	e.printStackTrace();
		//}
	
		return folder;
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


	public static void deploy(File folder) throws IOException, ApiException {
	
		System.out.println("Deploying application on Kubernetes...");
		
		// FALTA DESPLEGARLOS DESDE EL ULTIMO COMPONENTE AL PRIMERO
		// El orden yo lo pondria asi:
		//		1. Componentes que tengan peticiones de servicios (Service) y que solo tengan inPort (p.e. Sink eXist)
		//		2. Componentes que tengan peticiones de servicios (Service) y que tengan inPort y outPort (p.e. Processing OEE)
		//		3. Componentes que no tengan peticiones de servicios (p.e. Source MQTT-HTPP)
		
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
					V1Deployment newDeploy = null;
					if (isDeployInCluster(appsAPI, deployBody.getMetadata().getName()))
						newDeploy = appsAPI.replaceNamespacedDeployment(deployBody.getMetadata().getName(),"default", deployBody, null, null);
					else
						newDeploy = appsAPI.createNamespacedDeployment("default", deployBody, Boolean.FALSE, null, null);
					
					System.out.println(" Deployed:  " + newDeploy.getMetadata().getName());
				
				} else if (map.get("kind").equals("Service")) {
					V1Service svcBody = (V1Service) yaml.loadAs(fr, V1Service.class);
					System.out.println("---" + svcBody.getKind());
					System.out.println("---" + svcBody.getMetadata().getName());
					
					// Al convertir con Kompose se convierte mal el TargetPort: tiene que ser int, con String no funciona
					int targetPort = Integer.parseInt(svcBody.getSpec().getPorts().get(0).getTargetPort().getStrValue());
					svcBody.getSpec().getPorts().get(0).setTargetPort(new IntOrString(targetPort));
					
					System.out.println("\n Deploying new Service...");
					V1Service newSvc = null;
					if (isServiceInCluster(coreAPI, svcBody.getMetadata().getName()))
						newSvc = coreAPI.replaceNamespacedService(svcBody.getMetadata().getName(), "default", svcBody, null, null);
					else
						newSvc = coreAPI.createNamespacedService("default", svcBody, null, null, null);
					System.out.println(" Deployed:  " + newSvc.getMetadata().getName());
				}
				
				fr.close();
				input.close();
			}
		}
	}
	
	
	private static boolean isDeployInCluster(AppsV1Api appsAPI, String deployName) throws ApiException {
		
		V1DeploymentList allDeployments = appsAPI.listNamespacedDeployment("default", null, null, null, null, null, null, null, null, Boolean.FALSE);
		
		for (V1Deployment deploy: allDeployments.getItems()) {
			
			if (deployName.equals(deploy.getMetadata().getName()))
					return true;
		}
		
		return false;
		
	}
	
	private static boolean isServiceInCluster(CoreV1Api coreAPI, String svcName) throws ApiException {
		
		V1ServiceList allServices = coreAPI.listNamespacedService("default", null, null, null, null, null, null, null, null, Boolean.FALSE);
		
		
		for (V1Service service: allServices.getItems()) {
			
			if (svcName.equals(service.getMetadata().getName()))
					return true;
		}
		
		return false;
		
	}
	
	
}
