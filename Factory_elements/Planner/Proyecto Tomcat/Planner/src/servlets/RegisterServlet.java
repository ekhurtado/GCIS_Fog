package servlets;

import java.io.BufferedReader;
import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import elements.Planner;

/**
 * Servlet implementation class RegisterServlet
 */
@WebServlet("/RegisterServlet")
public class RegisterServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public RegisterServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		
		System.out.println("---> RegisterServlet doGet()");
		
//		response.getWriter().append("Served at: ").append(request.getContextPath());
		
		String servletPath = request.getServletPath();
		System.out.println("Servlet: " + servletPath);
		
		if (servletPath.contains("register")) {
			if (servletPath.split("/").length > 2) {
				if (servletPath.split("/")[2].equals("application")) {
					// Get Resquest Body
				    BufferedReader br = request.getReader();
				    StringBuilder requestBody = new StringBuilder();
				    while(br.ready()){
				    	requestBody.append((char) br.read());
			        }
				    
				    String ID = Planner.getInstance().appRegister(requestBody.toString());
				    
				    response.getWriter().append("New application ID: " + ID);
			    }
			}
		}
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		System.out.println("---> RegisterServlet doPost()");
		
		doGet(request, response);
	}

}
