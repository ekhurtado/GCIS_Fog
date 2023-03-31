Esta carpeta contiene los ficheros de la segunda parte de la cuarta versión de los controladores del sistema.  En este caso, en esta versión se han añadido, además de los existentes de Aplicación y Componente, los controladores de los niveles superiores.

Estos controladores superiores serán genéricos y el usuario será capaz de crear tantos niveles como desee, aunque todos estos tendrán la misma funcionalidad.

Se han diseñado para que la creación de estos se realice de forma jerárquica, es decir, definiendo el mayor nivel superior, los controladores de cada nivel serán capaces de crear los recursos del nivel inferior.

En esta parte se ha modificado el atributo flowConfig para habilitar añadir mas de un componente previo y posterior, así ofreciendo la posibilidad de diseñar aplicaciones más complejas. Además, el dato del tópico IFMH se ha movido dentro de esta especificación, para que se sitúe junto al nombre del componente asociado.