import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.zip.GZIPOutputStream;

import org.apache.commons.compress.archivers.ArchiveOutputStream;
import org.apache.commons.compress.archivers.ArchiveStreamFactory;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;
import org.apache.commons.compress.utils.IOUtils;

import com.google.api.gax.paging.Page;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.Bucket;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import com.google.common.collect.Lists;

public class ComponentCreator {
	
	public static void main(String[] args) throws Exception {
		System.out.println("I am component creator");
		
		System.out.println("Executing shell command...");
		
		String dockerfile = "FROM tomcat:jdk8-openjdk\r\n" + 
				"\r\n" + 
				"WORKDIR /\r\n" + 
				"\r\n" + 
				"EXPOSE 8080\r\n" + 
				"\r\n" + 
				"CMD [\"catalina.sh\", \"run\"]";
		
		
		String cmd = "curl --unix-socket /var/run/docker.sock -H \"Content-Type: application/x-tar\" --data-binary '@Dockerfile2.tar.gz' "
				+ "-X POST \"http://localhost/v1.41/build?t=gcr.io/clusterekaitz/pruebas-gcis:nuevo2&dockerfile=Dockerfile_2\"";
//		String cmd ="ifconfig";
		executeCMD(cmd);
		
//		authExplicit("C:\\Users\\839073\\Downloads\\clusterekaitz-007155af0d57.json");
		
		
//		buildImage(dockerfile, "gcr.io/clusterekaitz/pruebas-gcis:nuevo2");
	}
	
	public static void authExplicit(String jsonPath) throws IOException {
	  // You can specify a credential file by providing a path to GoogleCredentials.
	  // Otherwise credentials are read from the GOOGLE_APPLICATION_CREDENTIALS environment variable.
	  GoogleCredentials credentials = GoogleCredentials.fromStream(new FileInputStream(jsonPath))
	        .createScoped(Lists.newArrayList("https://www.googleapis.com/auth/cloud-platform"));
	  Storage storage = StorageOptions.newBuilder().setCredentials(credentials).build().getService();

	  System.out.println("Buckets:");
	  Page<Bucket> buckets = storage.list();
	  for (Bucket bucket : buckets.iterateAll()) {
	    System.out.println(bucket.toString());
	  }
	}
	
	public static void executeCMD(String cmd) throws Exception {
		
		System.out.println("Executing: " + cmd);
		
		Runtime run = Runtime.getRuntime();
		Process pr = run.exec(cmd);
		pr.waitFor();
		BufferedReader buf = new BufferedReader(new InputStreamReader(pr.getInputStream()));
		String line = "";
		while ((line=buf.readLine())!=null) {
			System.out.println(line);
		}
	}
	
	public static String buildImage(String dockerfile, String tag) throws Exception {
		String result = "OK";
		
		System.out.println("Building image...");
		
		// 1. Crear el archivo Dockefile
//		File tmpFile = new File("C:\\Users\\839073\\Documents\\System Model Component\\Dockerfile");
		File tmpFile = new File("Dockerfile");
	    FileWriter writer = new FileWriter(tmpFile);
	    writer.write(dockerfile);
	    writer.close();
	    
	    // 2. Crear el archivo comprimido
	    
        OutputStream tar_output = new FileOutputStream(new File("C:\\Users\\839073\\Documents\\System Model Component\\Dockerfile.tar.gz"));
//	    OutputStream tar_output = new FileOutputStream(new File("Dockerfile.tar.gz"));
        ArchiveOutputStream my_tar_ball = new ArchiveStreamFactory().createArchiveOutputStream(ArchiveStreamFactory.TAR, tar_output);
        
        File tar_input_file= new File("Dockerfile");
        TarArchiveEntry tar_file = new TarArchiveEntry(tar_input_file);
        tar_file.setSize(tar_input_file.length());
        my_tar_ball.putArchiveEntry(tar_file);
        IOUtils.copy(new FileInputStream(tar_input_file), my_tar_ball);
        
        my_tar_ball.closeArchiveEntry();
        my_tar_ball.finish(); 
        tar_output.close();
        
        
        // 3. Enviar mensaje HTTP
		String urlString = "http://192.168.233.130/v1.41/build";
		urlString = urlString + "?t=" + tag + "&localSocket=/var/run/docker.sock";
		
		URL url = new URL(urlString);
    	HttpURLConnection connect = (HttpURLConnection) url.openConnection();
        connect.setRequestMethod("POST");
        connect.setDoOutput(true);
        
        connect.setRequestProperty("Content-Type", "application/x-tar");
        File f = new File("C:\\Users\\839073\\Documents\\System Model Component\\Dockerfile.tar.gz");
        OutputStream output = connect.getOutputStream();
        Files.copy(f.toPath(), output);
        output.flush(); 
	
		int status = connect.getResponseCode();
		String statusMessage = connect.getResponseMessage();
		System.out.println("Message to " + urlString);
		System.out.println("   <-- Status: " + status);
		System.out.println("   <-- Status Message: " + statusMessage);
		
		String responseMessage = getResponseMessage(connect);
		System.out.println("   <-- Response Message: " + responseMessage);
		
		return result;
	}
	
	private static String getResponseMessage(HttpURLConnection connect) throws IOException {

		InputStream is = connect.getInputStream();
	    BufferedReader rd = new BufferedReader(new InputStreamReader(is));
	    StringBuilder response = new StringBuilder();
	    String line;
	    while ((line = rd.readLine()) != null) {
	      response.append(line);
	    }
	    rd.close();
	    
	    return response.toString();
	}
	
	

}
