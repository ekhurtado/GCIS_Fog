Esta carpeta contiene los ficheros de la tercera versión de los controladores de los niveles de Aplicación y Componente. En este caso, esta versión es una traducción al inglés de la versión 2, tanto en los conceptos de recurso como las muestras por pantalla (eventos, estado, etc.).

Por otro lado, se han diseñado los controladores para que sean capaces de hacer un seguimiento de los recursos, añadiendo el ciclo de despliegue y vida de estos mediante el apartado status y al conseguir información de estos mediante el CLI.

Además, contiene las nuevas definiciones de los componentes permanentes, los cuales utilizan los elementos "ConfigMap" de Kubernetes para actualizar dinámicamente su participación en las aplicaciones, incluso en runtime.

En el controlador de componentes se han añadido los archivos de despliegue personalizables para las aplicaciones de adquisición y procesamiento de datos, con los parámetros necesarios en cada caso.