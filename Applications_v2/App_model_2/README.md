Esta carpeta contiene los ficheros necesarios para desplegar las aplicaciones de adquisición y procesamiento de datos.

En este caso, se trata del modelo 2: dos aplicaciones para cada tipo (2 de adquisición y dos de procesamiento) pero que comparten componentes persistentes. En este

Al ser aplicaciones dependientes entre sí, cada una tendrá una key en la comunicación asíncrona de Kafka para identificar a la aplicación. El componente persistente. en este caso el componente _processing_oee_, recogerá los datos de las dos aplicaciones, y enviará el key la aplicación que corresponde en cada caso.