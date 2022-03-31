package utilities;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Scanner;

import com.jcraft.jsch.ChannelExec;
import com.jcraft.jsch.ChannelSftp;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.jcraft.jsch.SftpException;

public class ComponentCreator {
	
	// Singleton pattern
    private static ComponentCreator instance = new ComponentCreator();
    
    private String user = "gcis";
	private String password = "gcis";
	private String host = "192.168.233.132";
	private int port = 22;
	
	private Session session;
    
    private ComponentCreator() {

    }

    public static ComponentCreator getInstance() {
        return instance;
    }
    
    
	//////////////////////////////
	// SSH methods
	//////////////////////////////
	private void connectSSH() {
		
		try {
			
            JSch jsch = new JSch();
            session = jsch.getSession(user, host, port);
            session.setPassword(password);
            session.setConfig("StrictHostKeyChecking", "no");
            System.out.println("Establishing Connection...");
            session.connect();
            System.out.println("Connection established.");
            
        } catch (JSchException e) {
            e.printStackTrace();
        }
	}
	
	private void disconnectSSH() {
		session.disconnect();
	}
	
	private String getFile(String filePath) throws JSchException, SftpException {
		
		ChannelSftp sftpChannel = (ChannelSftp) session.openChannel("sftp");
        sftpChannel.connect();
        System.out.println("SFTP Channel created.");

        InputStream inputStream = sftpChannel.get(filePath);
        String line = null;
        try (Scanner scanner = new Scanner(new InputStreamReader(inputStream))) {
            while (scanner.hasNextLine())
                line = scanner.nextLine();
        }
        
        sftpChannel.disconnect();
        
        return line;
        
	}
	
	private String executeCommand(String command) throws JSchException, IOException {
		
		System.out.println("Executing command: " + command);

        ChannelExec channelExec = (ChannelExec) session.openChannel("exec");
   	 	InputStream in = channelExec.getInputStream();
   	 	
        // Ejecutamos el comando.
        channelExec.setCommand(command);
        channelExec.connect();
        
        // Obtenemos el texto impreso en la consola.
        BufferedReader reader = new BufferedReader(new InputStreamReader(in));
        StringBuilder builder = new StringBuilder();
        String linea;
		while ((linea = reader.readLine()) != null) {
		    builder.append(linea + "\n");
		}

        // Cerramos el canal SSH.
        channelExec.disconnect();
        
        return builder.toString();
	}
    
    
	//////////////////////////////
	// Docker methods
	//////////////////////////////
	private String createDockerfile(String compID, String dockerfile) throws IOException {
    	
    	
    	File file = new File("/system_model/dockerfiles/Dockerfile_"+ compID);
	    FileWriter writer = new FileWriter(file);
	    writer.write(dockerfile);
	    writer.close();
	    
	    // Si creamos un archivo por SSH tenemos que darle permisos para todos los usuarios
    	file.setReadable(true, false);
    	file.setWritable(true, false);
	    
	    return file.getAbsolutePath();
    }
    
    
    private String createImage(String applicationID, String componentID, String dockerfileName) {
    	
    	String build = null;
		try {
			build = executeCommand("docker build -t gcr.io/clusterekaitz/" +applicationID+ ":" +componentID+ " -f " +dockerfileName+ " /system_model/dockerfiles/");
		} catch (JSchException | IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	    if (build.contains("Successfully tagged"))
	    	return "gcr.io/clusterekaitz/" +applicationID+ ":" +componentID;
	    else
	    	return "ERROR: failed to create Docker image.";
    }
    
    private String pushImage(String imageName) {
    	
    	String pushResult = null;
		try {
			pushResult = executeCommand("docker push " + imageName);
		} catch (JSchException | IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		if ((pushResult.contains("An image does not exist locally with the tag")) || (pushResult.contains("invalid reference format")) || (pushResult.equals("")))
			return "ERROR: failed to push image to Google Container Registry.";
		else
			return "OK";
    }
    
    
	//////////////////////////////
	// Other methods
	//////////////////////////////
    
    public String buildComponent(String applicationID, String componentID, String dockerfile) {
    	
    	// TODO BORRAR
    	System.out.println("Building component " + componentID + " of app " + applicationID);
    	
    	// Primero, estableceremos la conexion con la maquina remota (con Docker y GCloud) via SSH
    	connectSSH();
    	
    	// Hay que crear el archivo Dockerfile para poder construir la imagen Docker
    	String dockerfilePath  = null;
    	try {
    		dockerfilePath = createDockerfile(componentID, dockerfile);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			disconnectSSH();
			return "ERROR: Cannot create Dockerfile of component " + componentID + " of application " + applicationID;
		}
    	
    	// Despues, construiremos la imagen Docker
    	String imageName = createImage(applicationID, componentID, dockerfilePath);
    	if (imageName.contains("ERROR")) {
    		disconnectSSH();
    		return imageName;
    	}
    	
    	// Teniendo la imagen creada, la subiremos al repositorio (registro de imagenes)
    	System.out.println("Pushing image " + imageName);
    	String push = pushImage(imageName);
    	if (push.contains("ERROR")) {
    		disconnectSSH();
    		return push;
    	}
    	
    	// Finalmente, nos desconectaremos de la maquina remota
    	disconnectSSH();
    	
    	return imageName;
    }

	public void deleteComponent(String imageName) {
		
		// TODO BORRAR
    	System.out.println("Deleting component " + imageName);
		
		// Primero, estableceremos la conexion con la maquina remota (con Docker y GCloud) via SSH
    	connectSSH();
    	
    	String commandToDelete = "gcloud container images delete " + imageName + " --quiet";
    	
    	try {
			executeCommand(commandToDelete);
		} catch (JSchException | IOException e) {
			e.printStackTrace();
		}
    	
    	// Finalmente, nos desconectaremos de la maquina remota
    	disconnectSSH();
		
	}
	

}
