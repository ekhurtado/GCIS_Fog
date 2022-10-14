Esta carpeta contiene ficheros de pruebas para desplegar un controlador de aplicaciones en Kubernetes.

Contiene la primera versión de pruebas de concepto de los diferentes pasos a seguir.

Tres maneras de funcionar en este momento:

- Utilizar el fichero "mi_controlador_aplicaciones.py", de esta forma, se incorporará el CRD de aplicación y se iniciará el controlador. Después, con el script "solicitar_nueva_aplicacion.py", podemos añadir aplicaciones en Kubernetes.
	
- Utilizar "mi_controlador_componentes.py" y "mi_controlador_aplicaciones_v2.py". De esta forma, tendremos componentes y aplicaciones como objetos en Kubernetes. El script para añadir aplicaciones sigue siendo válido "solicitar_nueva_aplicacion.py".

- Utilizar los ficheros de despliegue en "ficherosdocker". Después utilizar  "solicitar_nueva_aplicacion.py"

Es necesario descargar el resto de ficheros para disponer de todas las dependencias.
