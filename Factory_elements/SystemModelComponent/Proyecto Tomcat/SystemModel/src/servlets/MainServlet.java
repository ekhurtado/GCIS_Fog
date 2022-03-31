package servlets;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import components.SystemModel;

/**
 * Servlet implementation class MainServlet
 */
@WebServlet("/MainServlet")
public class MainServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	
	private SystemModel smc = null;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public MainServlet() {
        super();
        // TODO Auto-generated constructor stub
        
        smc = SystemModel.getInstance();
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		System.out.println("---> MainServlet doGet()"); 
		//TODO Auto-generated method stub
		StringBuilder generalResponse = new StringBuilder();
		generalResponse.append("Served at: ").append(request.getContextPath());
		generalResponse.append("\nServlet Path: ").append(request.getServletPath());
		generalResponse.append("\nHi! I am the System Model component.\n\n");
		generalResponse.append("\nI can register and validate elements of the fog:\n\n");
		generalResponse.append("\t-> Fog-in-the-loop applications.\n");
		generalResponse.append("\t-> Events and the actions related.\n");
		
		String servletPath = request.getServletPath();
		
		if (servletPath.equals("/")) {
			response.getWriter().append(generalResponse);
		} else {
					
			if (servletPath.contains("showSystem")) {
				try {
					String systemDef = SystemModel.getInstance().showSystem();
					response.getWriter().append(systemDef);
					
				} catch (Exception e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}  else if (servletPath.contains("register")) {
				if (servletPath.split("/").length > 2) {
				    
					String ID = null;
					String type = servletPath.split("/")[2];
					
					if (type.equals("systemElement")) {
						
						try {
							ID = SystemModel.getInstance().seRegister(getRequestBody(request));
						} catch (Exception e) {
							e.printStackTrace();
						}
						if (ID == null)
							response.getWriter().append("ERROR: The registration of the element could not be completed.\n");
						else
							response.getWriter().append(ID);
						
					} else if (type.equals("application")) {

						try {
							ID = SystemModel.getInstance().appRegister(getRequestBody(request));
						} catch (Exception e) {
							e.printStackTrace();
						}
						if (ID == null)
							response.getWriter().append("ERROR: The registration of the application could not be completed.\n");
						else
							response.getWriter().append(ID);
					}
				} else
					response.getWriter().append("ERROR: URL is not the correct one.\n");
			} else if (servletPath.contains("validate")) {
				if (servletPath.split("/").length > 2) {
				    
					String result = "";
					String type = servletPath.split("/")[2];
					
					if (type.equals("application")) {
						try {
							result = SystemModel.getInstance().validateApp(getRequestBody(request));
						} catch (Exception e) {
							e.printStackTrace();
						}
						if (result == null)
							response.getWriter().append("ERROR: The application could not be validated.");
						else
							response.getWriter().append(result);
							
					}
				}
			} else if (servletPath.contains("start")) {
				if (servletPath.split("/").length > 2) {
				    
					String result = "";
					String type = servletPath.split("/")[2];
					
					if (type.equals("application")) {
						try {
							result = SystemModel.getInstance().appStart(getRequestBody(request));
						} catch (Exception e) {
							e.printStackTrace();
						}
						if (result == null)
							response.getWriter().append("ERROR: The application could not be started.");
						else {
//							result = result.replace("\n", "\\n");
							response.getWriter().append(result);
						}
							
					}
				}
			} else if (servletPath.contains("list")) {
				response.getWriter().append(SystemModel.getInstance().list(""));
			} else if (servletPath.contains("delete")) {
				response.getWriter().append(SystemModel.getInstance().deleteElement(getRequestBody(request)));
			}
			
		}
		
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		System.out.println("---> MainServlet doPost()");
		doGet(request, response);
	}
	
	
	//////////////////
	// Other methods
	//////////////////
	private String getRequestBody(HttpServletRequest request) throws IOException {
		// Get Request Body
	    BufferedReader br = request.getReader();
	    StringBuilder requestBody = new StringBuilder();
	    while(br.ready()){
	    	requestBody.append((char) br.read());
        }
	    
	    return requestBody.toString();
	}

}
