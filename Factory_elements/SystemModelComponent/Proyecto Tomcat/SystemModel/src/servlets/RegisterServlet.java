package servlets;

import java.io.BufferedReader;
import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import components.Planner;
import components.SystemModel;

/**
 * Servlet implementation class RegisterServlet
 */
@WebServlet("/RegisterServlet")
public class RegisterServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	
	private SystemModel systemModel = null;
	
	private Planner planner = null;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public RegisterServlet() {
        super();
        // TODO Auto-generated constructor stub
        
        systemModel = SystemModel.getInstance();
        planner = Planner.getInstance();
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		System.out.println("---> RegisterServlet doGet()");
		
//		response.getWriter().append("Served at: ").append(request.getContextPath());
//		response.getWriter().append("\nHi! I am the System Model component.\n\n");
//		response.getWriter().append("\nThis is the service to register and validate elements of the fog.\n");
		
		// Get Resquest Body
	    BufferedReader br = request.getReader();
	    StringBuilder payload = new StringBuilder();
	    while(br.ready()){
	    	payload.append((char) br.read());
        }
	    
	    System.out.println(payload);
	    
		String newID = planner.appRegister(payload.toString());
		if (newID == null)
			response.getWriter().append("The application has not been registered.");
		else
			response.getWriter().append("The application has been registered successfully. New ID: " + newID);
		
		
		/*
		 * PASOS PARA REGISTRAR UNA APLICACION
		 * 
		 * 1. Se recibe el mensaje HTTP y se consigue el XML del contenido
		 * 2. El XML se convierte en un objeto en JAVA-> ArrayList<ArrayList<ArrayList<String>>>
		 * 		- En FlexManSys-> Linea 170 del Planner
		 * 		- Si es encesario, cambiar el objeto de JAVA para solo quedarnos con los datos buenos
		 * 3. Por cada elemento:
		 * 		3.1. Crea la estructura de atributos de ese elemento
		 * 		3.2. Se lo envia al SystemModelAgent?
				 * 4. En el System Model:
				 * 		4.1. Procesa los atributos recibidos
				 * 		4.2. Comprueba si existe el tipo de componente
				 * 		4.3. Valida la definicion del componente
				 * 		4.4. Lo valida contra el esquema XSD
				 * 		4.5. Si es correcto, se registra el componente en el System Model
		 * 5. Al finalizar, estará la aplicacion completa registrada
		 */
		
		/*
		 * En FlexManSys:
		 * 
		 * 	- Los planes de fabricacion se registran nivel a nivel (mplan, order, batch...)
		 *  - Primero valida la jerarquia (AppHierarchy.xsd)
		 *  - Despues valida si el tipo de elemento tiene los datos necesarios (AppProperties.xsd)
		 *  - Registra despues de validar la jerarquia, y si despues de eso el elemento no es correcto, lo elimina
		 *  
		 *  Tipos de datos:
		 *  	1. En el Planner se decide un plan de fabricacion, que consiste de un archivo XML (MPlan1.xml)
		 *  	2. Utilizan la herramienta XMLReader.readFile() para pasar de un archivo XML a un objeto ArrayList<ArrayList<ArrayList<String>>>
		 *  	3. Utilizan MPlanInterpreter.getManEntities() para quedarse con la informacion util, y asi reordenar las listas
		 *  	4. Recorren las listas del objeto para conseguir sus atributos y enviarselos al System Model para su registro y validacion
		 *  
		 *  Que diferencia hay entre validad "hierarchy" (linea 1236) o "appValidation" (linea 716)? "appValidation" solo se hace con el primer elemento (mplan) ?
		 */
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
