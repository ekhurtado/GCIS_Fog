package servlets;

import java.io.BufferedReader;
import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import components.EventManager;;

/**
 * Servlet implementation class MainServlet
 */
@WebServlet("/MainServlet")
public class MainServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public MainServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		StringBuilder generalResponse = new StringBuilder();
		generalResponse.append("Served at: ").append("Hi ! \n I am the Event Manager resource.\n");
		generalResponse.append("Served at: ").append(request.getContextPath());
		generalResponse.append("\nServlet Path: ").append(request.getServletPath());
		
		String servletPath = request.getServletPath();
		
		if (servletPath.equals("/")) {
			response.getWriter().append(generalResponse);
		} else {
			if (servletPath.contains("deploy")) {
				if (servletPath.split("/").length > 2) {
				    
					String ID = null;
					String type = servletPath.split("/")[2];
					
					String appID = response.getHeader("applicationID");
					
					if (type.equals("application")) {
						
						try {
							ID = EventManager.getInstance().appDeploy(getRequestBody(request), appID);
						} catch (Exception e) {
							e.printStackTrace();
						}
						if (ID == null)
							response.getWriter().append("ERROR: The registration of the element could not be completed.\n");
						else
							response.getWriter().append(ID);
						
					}
}
			}
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
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
