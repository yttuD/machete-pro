# Conceptos Base - Asistente de IA

## Seguridad en bases de datos
Es el conjunto de políticas, procedimientos y controles que permiten proteger los datos frente a accesos no autorizados, corrupción o pérdida. Para garantizarla, se aplican diversos mecanismos como la autenticación de usuarios, la gestión de permisos y roles, el cifrado de datos y el registro de auditoría, además de implementar estrategias para prevenir ataques como inyecciones SQL, accesos indebidos y corrupción de datos.

## La regla de la triple A+C
Son los componentes principales de la seguridad en las bases de datos: Autenticación, Autorización, Auditoría y Control de Acceso.

## Autenticación
Es el proceso mediante el cual un sistema verifica que un usuario es quien dice ser, realizándose generalmente a través de credenciales como un nombre de usuario y una contraseña. En bases de datos, asegura que solo personas autorizadas puedan establecer una conexión con el SGBD.

## Autorización
Determina qué acciones puede realizar un usuario una vez autenticado, controlando su nivel de acceso a los objetos (por ejemplo, qué tablas puede ver, modificar, crear o eliminar) mediante la asignación de permisos específicos (GRANT).

**Ejemplo SQL:** `GRANT SELECT, INSERT ON empresa.facturas TO 'usuario_ventas'@'localhost';` (permite leer e insertar, pero no eliminar).

## Auditoría
Es el proceso de registrar y monitorear las acciones realizadas por los usuarios dentro del sistema, incluyendo detalles sobre quién accedió, cuándo y qué datos consultó o modificó. Es clave para la trazabilidad, detección de incidentes de seguridad y cumplimiento de normativas.

**Ejemplo SQL:** En MySQL se habilita con `SET GLOBAL general_log = 'ON';`.

## Control de acceso
Se refiere a la definición y asignación de privilegios a los usuarios, habitualmente organizados por roles (los cuales agrupan un conjunto de permisos para facilitar la administración de múltiples usuarios con funciones similares).

**Metáfora:** Los roles son como un "carnet de acceso" general. En lugar de dar una llave individual para cada puerta (permiso), entregas un carnet que ya incluye los accesos autorizados.

## Integridad de datos
Se refiere a la exactitud, coherencia y confiabilidad de los datos almacenados en una base de datos. Significa que los datos no han sido alterados o dañados de manera indebida y que se mantienen correctos a lo largo del tiempo mediante reglas y controles que evitan errores, duplicaciones o modificaciones incorrectas. Según Elmasri y Navathe, es la propiedad que garantiza la corrección y validez de los datos, asegurando que cumplan con restricciones predefinidas y evitando inconsistencias.
Según Elmasri y Navathe (2016), la integridad de datos es "la propiedad que garantiza la corrección y validez de los datos en la base de datos, asegurando que cumplan con restricciones predefinidas y evitando inconsistencias"

## Integridad de entidad
Asegura que cada fila en una tabla sea única y pueda identificarse sin ambigüedades. Se logra mediante el uso de claves primarias (PRIMARY KEY), que son campos o conjuntos de campos que no pueden repetirse ni tener valores nulos.

## Integridad referencial
Se encarga de mantener relaciones correctas entre tablas mediante el uso de claves foráneas (FOREIGN KEY), asegurándose de que los valores en una columna de una tabla coincidan con los valores de una clave primaria en otra tabla.

## Integridad de dominio
Controla que los valores almacenados en un campo sean correctos y lógicos utilizando restricciones como CHECK (define condiciones a cumplir), NOT NULL (obliga a que un campo siempre tenga un valor) y UNIQUE (evita valores repetidos en una columna).

## Integridad personalizada
Consiste en reglas avanzadas definidas por el usuario que permiten ejecutar acciones automáticamente cuando ocurre un cambio en la base de datos, implementadas típicamente mediante triggers (disparadores) y reglas.

## Transacción
Es un grupo de operaciones que deben ejecutarse juntas como una unidad indivisible. Si todas las operaciones se completan con éxito, la transacción se confirma (COMMIT); pero si algo falla en el proceso, la transacción se revierte (ROLLBACK), dejando la base de datos en el estado en que estaba antes de comenzar.

## Propiedades ACID
Son las cuatro propiedades esenciales que deben cumplir las transacciones para garantizar la coherencia y seguridad de los datos:
* **Atomicidad**: Principio de "todo o nada". Si una parte de la transacción falla, se revierte por completo.
* **Consistencia**: Garantiza que los datos se mantengan correctos y válidos antes y después de la transacción.
* **Aislamiento**: Asegura que cada transacción ocurra de forma independiente, sin afectar ni ser afectada por otras transacciones en ejecución concurrente.
* **Durabilidad**: Garantiza que una vez confirmada la transacción, los cambios persistan de forma permanente en el sistema, incluso ante fallos de este.

## BEGIN TRANSACTION / START TRANSACTION
Comando que inicia una transacción, indicándole a la base de datos que a partir de ese punto cualquier cambio (INSERT, UPDATE, DELETE) no se guardará de inmediato de manera definitiva, sino que esperará una confirmación.

## COMMIT
Comando que confirma la transacción actual, guardando todos los cambios realizados en la base de datos de forma definitiva y permanente.

## ROLLBACK
Comando que cancela la transacción actual en caso de un problema o error, deshaciendo todos los cambios realizados desde el inicio de la transacción y devolviendo los datos a su estado original.

## Bloqueo (Lock)
Es una restricción temporal aplicada por el SGBD que evita que dos o más transacciones accedan o modifiquen el mismo dato de forma simultánea, previniendo así problemas de concurrencia y manteniendo la integridad de los datos.

## Lectura sucia (Dirty Read)
Problema de concurrencia que ocurre cuando una transacción lee datos modificados por otra transacción que aún no ha sido confirmada (y que, por lo tanto, podrían ser revertidos mediante un ROLLBACK).

## Lectura no repetible (Non-Repeatable Read)
Problema de concurrencia que ocurre cuando una consulta obtiene diferentes resultados en dos ejecuciones distintas dentro de una misma transacción, debido a que otra transacción modificó y confirmó los datos en el intervalo entre ambas lecturas.

## Lectura fantasma (Phantom Read)
Problema de concurrencia que ocurre cuando una transacción realiza una consulta de un conjunto de filas varias veces y, en el transcurso, otra transacción inserta o elimina registros que cumplen con las condiciones de la búsqueda, alterando el resultado final obtenido en las lecturas subsiguientes.

## Bloqueo exclusivo (Exclusive Lock - X Lock)
Tipo de bloqueo que se aplica cuando una transacción va a modificar un dato. Mientras se encuentra activo, ninguna otra transacción puede leer ni modificar dicho dato.

## Bloqueo compartido (Shared Lock - S Lock)
Tipo de bloqueo que se utiliza cuando una transacción solo va a leer un dato. Permite que múltiples transacciones lean el dato simultáneamente, pero impide que cualquiera de ellas lo modifique hasta que se liberen todos los bloqueos compartidos sobre él.

## Índices en un SGBD
Son estructuras de datos auxiliares creadas sobre una o más columnas que permiten acelerar el acceso a los datos de una tabla. Funcionan de manera similar a los índices de los libros, facilitando la localización rápida de registros sin necesidad de realizar un recorrido completo de la tabla (lo que optimiza el tiempo de lectura), aunque implican un costo adicional de espacio y de rendimiento en las operaciones de escritura (INSERT, UPDATE, DELETE), ya que deben mantenerse actualizados constantemente.

**Metáfora:** Buscar registros sin un índice es como recorrer una biblioteca estante por estante sin un catálogo. Un índice es la lista alfabética de autores en la entrada que te indica en qué estante exacto está el libro.

## CREATE INDEX
Comando en SQL que se utiliza para crear una estructura de índice sobre una o varias columnas de una tabla con el fin de agilizar las consultas y búsquedas de información que filtran por dichas columnas.

## DROP INDEX
Comando en SQL empleado para eliminar un índice existente de una tabla cuando ya no es necesario, o cuando la penalización de rendimiento que genera en las modificaciones y actualizaciones de los datos es mayor que el beneficio que aporta en las lecturas.

## Índice B-TREE
Es el tipo de índice más utilizado por los SGBD relacionales (como MySQL, PostgreSQL y Oracle) que organiza los datos en forma de árbol balanceado. Permite búsquedas, inserciones y eliminaciones muy eficientes, resultando ideal para columnas que se emplean frecuentemente en búsquedas de rango, ordenamientos o filtros (WHERE, ORDER BY, BETWEEN, >, <).

## Índice ÚNICO
Tipo de índice que no permite valores duplicados en la columna o combinación de columnas sobre las que se aplica. Se utiliza principalmente para asegurar y garantizar la unicidad de datos clave en el negocio, tales como números de documentos de identidad (DNI), nombres de usuario o correos electrónicos.

## Índice COMPUESTO
También denominado índice multicolumna, es un índice que se crea sobre más de una columna a la vez. Sirve para mejorar sustancialmente el rendimiento de las consultas que realizan filtros simultáneos por varias columnas, teniendo en cuenta que el orden en el que se declaran las columnas al crear el índice es sumamente significativo para su eficiencia.

## Índice HASH
Es un tipo de índice que utiliza una función hash para asociar de manera directa una clave a los valores indexados, ofreciendo búsquedas sumamente rápidas pero únicamente para comparaciones de igualdad exacta (=). No es de utilidad para búsquedas de rangos ni para operaciones de ordenamiento.

## Vistas en un SGBD
Son objetos virtuales que resultan de una consulta almacenada en el sistema gestor de bases de datos. Aunque se comportan como si fueran tablas, no almacenan datos de manera física ni permanente. Su principal objetivo es simplificar y reutilizar consultas complejas, restringir o proteger el acceso a columnas con datos sensibles y proporcionar diferentes perspectivas de los mismos datos subyacentes.

## Vista simple
Tipo de vista que se basa en una única tabla, no incluye funciones agregadas ni agrupamientos (GROUP BY) y permite de manera general modificar o actualizar los datos de la tabla base a través de ella si no existen restricciones adicionales. Funciona como un filtro que muestra solo ciertas filas o columnas.

**Metáfora:** Una vista simple es como un formulario estructurado para consultar datos específicos sin ver toda la base original.

## Vista compleja
Es una vista que involucra la combinación de múltiples tablas mediante uniones (JOINS), subconsultas, cálculos o el uso de funciones de agregación y agrupamientos. A diferencia de la vista simple, usualmente no permite modificar los datos de origen directamente a través de ella.

## Vista materializada
Es un tipo de vista que sí almacena físicamente en el disco los resultados obtenidos de la consulta, funcionando como una "fotografía" estática de los datos. Mejora drásticamente el rendimiento de consultas muy pesadas porque evita tener que recalcular los resultados cada vez que se ejecuta, pero tiene la desventaja de que no se actualiza automáticamente en tiempo real ante cambios en las tablas base, requiriendo un refresco (REFRESH) programado o manual para sincronizarse.

**Metáfora:** Una vista materializada es como una "fotografía" de los datos impresa en papel: es instantánea de leer, pero no cambia si el paisaje original (tabla base) cambia.

## CREATE VIEW
Comando en SQL que se utiliza para definir y almacenar una vista en el SGBD, asociándola a una instrucción de consulta SELECT específica sin que esto altere físicamente las tablas origen.

## Normalización de bases de datos
Es una técnica de diseño lógico que permite estructurar las tablas de manera eficiente con el fin de reducir la redundancia de datos y evitar anomalías durante las operaciones de actualización, inserción y eliminación de información.

## Primera Forma Normal (1NF)
Regla de normalización que establece que una tabla está en 1NF si todos sus atributos contienen únicamente valores atómicos indivisibles, asegurando que cada campo tenga un solo valor por fila y eliminando por completo los grupos repetitivos o las listas de valores en una sola columna.

## Segunda Forma Normal (2NF)
Regla de normalización que requiere que la tabla ya cumpla con la 1NF y que todos sus atributos que no formen parte de la clave primaria dependan por completo de la clave primaria total. Su objetivo es eliminar las dependencias parciales, las cuales pueden presentarse únicamente cuando la clave primaria de la tabla es compuesta (formada por dos o más columnas).

## Clave compuesta
Es una clave primaria formada por la combinación de dos o más columnas que, de manera conjunta, permiten identificar de forma única y unívoca cada fila en una tabla, siendo necesaria cuando ninguna de las columnas por separado es suficiente para lograr dicha identificación.

## Dependencia parcial
Es una relación de dependencia que ocurre cuando un atributo no clave requiere de solo una parte de la clave primaria compuesta (y no de su totalidad) para determinar su valor.

## Tercera Forma Normal (3NF)
Regla de normalización que requiere que la tabla ya se encuentre en la 2NF y que ningún atributo que no sea clave dependa de forma transitiva (o indirecta) de la clave primaria. Esto implica que las columnas no clave no deben depender de otras columnas no clave.

## Dependencia transitiva
Ocurre cuando un atributo no clave depende de otro atributo no clave que, a su vez, depende de la clave primaria (es decir, una dependencia indirecta). Se debe evitar para impedir la duplicación de datos y facilitar actualizaciones seguras.

## Forma Normal de Boyce-Codd (BCNF)
Es una versión más estricta y rigurosa de la 3NF que busca eliminar redundancias remanentes causadas por dependencias funcionales. Se cumple si, para cada una de las dependencias funcionales de la relación ($X \rightarrow Y$), el determinante $X$ es una clave candidata de la tabla, sin admitir las excepciones que sí tolera la 3NF.

**Ejemplo:** Dependencia `Profesor -> Aula`. Si un Profesor no es clave primaria/candidata (porque enseña múltiples materias), pero determina el Aula, viola BCNF y debe separarse.

## Clave candidata
Conjunto de una o más columnas que puede identificar de forma única cada fila de una tabla. Aunque pueden existir múltiples alternativas válidas en una tabla, solo una de ellas se escoge como la clave primaria definitiva.

## Cuarta Forma Normal (4NF)
Nivel de normalización que exige que la tabla ya se encuentre en BCNF y que no contenga dependencias multivaluadas innecesarias o no triviales, evitando así combinaciones de datos independientes que generan repeticiones y redundancia en el diseño.

**Ejemplo:** Ana habla dos idiomas y practica dos deportes (sin relación entre sí). Esto genera combinaciones redundantes innecesarias. Se debe dividir en dos tablas: [Estudiante, Idioma] y [Estudiante, Deporte].

## Dependencia multivaluada ($X \rightarrow\rightarrow Y$)
Se presenta cuando la presencia de un valor en un atributo $X$ determina de forma independiente un conjunto de múltiples valores de otro atributo $Y$, sin importar qué valores tomen el resto de las columnas de la fila.

## Quinta Forma Normal (5NF) o de Proyección-Join
Es el nivel más alto de normalización y se aplica para resolver los problemas de dependencias de unión (join-dependencies). Una tabla está en 5NF si ya cumple con la 4NF y se garantiza que sus datos pueden ser divididos en múltiples relaciones y luego reconstruidos mediante JOINS sin perder información ni generar filas fantasma o combinaciones erróneas que no existían originalmente.

## Forma Normal de Dominio y Clave (DKNF)
Es el modelo teórico límite y más estricto de la normalización, en el cual se establece que una tabla está en DKNF si todas las restricciones sobre los datos pueden expresarse única y exclusivamente como restricciones de dominio (valores válidos para un campo) y restricciones de clave (valores que identifican filas de forma única), evitando cualquier anomalía residual de base de datos.

**Ejemplo (Regla de negocio vs Restricción):** "Si el empleado es Docente, su sueldo no puede ser menor a $300.000". Esto no es DKNF por defecto. Debe aplicarse mediante un `CHECK` explícito o rediseñando la tabla para que dependa estrictamente de un dominio o clave.

## Optimización de consultas
Es el proceso mediante el cual el motor de base de datos analiza estadísticas, índices y heurísticas para determinar el camino más eficiente y de menor costo para la ejecución de una sentencia SQL.

**Buenas Prácticas:**
* Evitar funciones sobre columnas indexadas (ej. `UPPER(nombre)`), ya que anulan el uso del índice.
* Evitar el uso de `SELECT *` para no cargar datos innecesarios en memoria.

## Plan de ejecución
Representación gráfica o textual que describe detalladamente los pasos técnicos y el recorrido que seguirá el motor de la base de datos para recuperar o modificar los datos solicitados en una consulta.

## EXPLAIN / EXPLAIN PLAN FOR
Comando utilizado en SGBD como PostgreSQL, MySQL o MariaDB que muestra el plan de ejecución estimado que el motor ha proyectado utilizar para resolver una consulta (sin ejecutar la sentencia real).

## EXPLAIN ANALYZE
Comando que, a diferencia de un EXPLAIN simple, ejecuta físicamente la consulta y recopila las estadísticas reales del plan de ejecución (tiempo consumido, filas analizadas y recursos utilizados).

## SET STATISTICS TIME ON
Comando específico de SQL Server que permite medir de forma exacta el tiempo de CPU y el tiempo total de ejecución empleado para resolver cada una de las instrucciones de una consulta SQL.

## Datos semiestructurados
Constituyen una categoría intermedia entre los datos estructurados (típicamente organizados en tablas relacionales) y los datos no estructurados (como imágenes, videos o textos libres). Se caracterizan por no ajustarse a un esquema rígido o tabular fijo, pero contienen etiquetas o marcadores que expresan una estructura jerárquica y describen la relación entre los datos y sus metadatos. Su esquema es flexible y puede evolucionar con rapidez sin necesidad de redefinir una base de datos por completo.


**Ejemplo:** Los formatos comunes como XML, JSON o YAML. Por ejemplo, en formato XML se puede representar a una persona con etiquetas específicas: `<nombre>Carla</nombre><edad>22</edad>`.
**Metáfora:** Son como una mochila flexible en la que puedes guardar diferentes objetos de tamaños y formas variables, reorganizando lo que llevas sin las restricciones de espacio que tendría un casillero escolar de tamaño fijo.
## XML (eXtensible Markup Language)
Es un metalenguaje diseñado para almacenar, estructurar e intercambiar información de manera legible tanto para humanos como para máquinas. Se trata de un formato autodescriptivo (cada elemento está etiquetado) y extensible (los usuarios definen sus propias etiquetas), complementario a HTML y de gran utilidad para lograr la interoperabilidad y el intercambio de datos entre diferentes plataformas, sistemas y lenguajes de programación.


**Ejemplo:**
```xml
<libro>
  <titulo>Introducción a la Programación</titulo>
  <autor>María Gómez</autor>
  <capitulo>
    <titulo>Variables y Tipos de Datos</titulo>
    <seccion>
      <titulo>Enteros y Reales</titulo>
      Los tipos numéricos básicos en programación...
    </seccion>
  </capitulo>
</libro>
```
**Metáfora:** Es como un contenedor etiquetado en un depósito: cada caja (elemento) tiene una etiqueta clara que explica qué contiene, dónde debe ir (jerarquía) y cómo debe combinarse con otras cajas para que todo el almacén esté organizado.
## Standard Generalized Markup Language (SGML)
Es un estándar internacional (ISO 8879) surgido en la década de 1980 para definir lenguajes de marcado y estandarizar la representación de documentos electrónicos complejos, logrando la independencia entre el contenido, la estructura lógica y la presentación visual. Sirve como un marco general del cual derivan directamente lenguajes más específicos como HTML y XML.


**Ejemplo:** SGML sirvió como base para la creación de lenguajes ampliamente conocidos como HTML y XML.
## DTD (Document Type Definition)
Es un conjunto de reglas sintácticas y de estructura que define de forma explícita qué elementos, atributos, jerarquías y combinaciones son válidos dentro de un documento XML o SGML. Funciona como una herramienta de validación para garantizar la coherencia, calidad e integridad de la información antes de ser procesada por una aplicación.


**Ejemplo:**
```xml
<!ELEMENT libro (titulo, autor, capitulo)>
<!ELEMENT titulo (#PCDATA)>
<!ELEMENT autor (#PCDATA)>
<!ELEMENT capitulo (titulo, seccion)>
<!ELEMENT seccion (titulo, #PCDATA)>
```
*(Donde `#PCDATA` representa datos de caracteres analizados, es decir, texto que puede incluir etiquetas).*
## DTD interno
Es la forma de validación en la que las reglas de estructura y definición del tipo de documento se incluyen directamente dentro del mismo archivo XML, declarándose en la sección de cabecera entre las etiquetas de tipo <!DOCTYPE ... [...]>.

## DTD externo
Es la modalidad de validación en la cual las reglas sintácticas se almacenan en un archivo independiente con extensión .dtd. Para que un documento XML pueda ser validado con este esquema, debe hacer referencia explícita al archivo externo mediante la declaración <!DOCTYPE ... SYSTEM "archivo.dtd">.

## Entidades en SGML
Son componentes de la DTD que funcionan como referencias o macros que permiten simplificar y estandarizar el uso de texto reutilizable dentro de un documento, evitando repetir contenido idéntico a lo largo de este.

## Validación de documentos XML/SGML
Es el proceso mediante el cual un procesador o editor especializado (como un navegador web o herramientas en línea) analiza un documento con marcas y comprueba de forma automatizada si cumple rigurosamente con las reglas de jerarquía, orden, atributos y elementos establecidas en su correspondiente DTD.


**Ejemplo:** Validar en línea ingresando a xmlvalidation.com, pegando el contenido de un XML, activando la opción "Use external DTD", subiendo el archivo .dtd correspondiente y ejecutando la validación para obtener el mensaje de éxito "The document is valid".
## Tecnologías NoSQL
Son tecnologías de almacenamiento de datos que no se basan en el modelo relacional tradicional ni utilizan esquemas rígidos de tablas y columnas. Están diseñadas para manejar datos que pueden ser no estructurados o semiestructurados.

## localStorage
Es un mecanismo de almacenamiento web local que permite a las aplicaciones guardar datos directamente en el navegador del usuario de forma persistente (sin fecha de expiración), resultando útil para registrar información local sin depender inicialmente de un servidor.

## MONGOSH
Es la interfaz de línea de comandos oficial (DBShell) utilizada para conectarse, interactuar, administrar y ejecutar consultas sintácticas directamente en un servidor de bases de datos MongoDB.

## Colección (en MongoDB)
Es la estructura equivalente a una tabla en las bases de datos relacionales, dentro de la cual se almacena un conjunto de documentos en formato BSON/JSON de manera flexible y sin un esquema rígido predefinido.

## Documento (en MongoDB)
Es la unidad básica de almacenamiento de información en MongoDB. Está compuesto por pares de clave-valor que se guardan en un formato estructurado similar a JSON, lo que permite albergar diversos tipos de datos, incluidos números, textos, booleanos, arreglos y subdocumentos anidados.

## Proyección (en MongoDB)
Es una operación técnica que se realiza durante las consultas para especificar exactamente qué campos del documento se desean recuperar o mostrar en el resultado de salida, utilizando el valor 1 para habilitar un campo y el valor 0 para ocultarlo.

## Operador $set
Es un operador de actualización en MongoDB que se utiliza para modificar o reemplazar el valor de un campo específico dentro de uno o varios documentos seleccionados sin alterar el resto de su contenido.

## Operador $inc
Es un operador de actualización empleado en MongoDB para incrementar o decrementar el valor de un campo numérico existente en una cantidad específica.

## Operador $gt
Es un operador de comparación en MongoDB que significa "mayor que" (greater than) y se utiliza para filtrar documentos cuyo campo evaluado sea numéricamente superior al valor de referencia especificado.

## Operador $lt
Es un operador de comparación en MongoDB que significa "menor que" (less than) y se utiliza para filtrar o eliminar documentos cuyo campo evaluado sea inferior al valor de referencia especificado.

## Operador $elemMatch
Es un operador de consulta en MongoDB que se utiliza para buscar y filtrar documentos que contienen un array, permitiendo seleccionar únicamente aquellos registros que tengan al menos un elemento en el array que cumpla simultáneamente con todos los criterios de búsqueda especificados.

## Sistemas de gestión de bases de datos impulsados por IA (Bases de datos autónomas)
También conocidos por sus siglas en inglés como SDDP (Self-Driving Database Platforms), son plataformas que aprovechan la inteligencia artificial y los algoritmos de aprendizaje automático para automatizar la optimización, el procesamiento de consultas, el ajuste del rendimiento y las tareas de mantenimiento rutinarias de las bases de datos. Su propósito es reducir la carga administrativa de los administradores de bases de datos (DBAs), permitiendo que el sistema perciba, tome decisiones y realice optimizaciones de forma independiente, tales como la gestión de recursos físicos, el ciclo de vida de las instancias, la seguridad y el escalado automático. Ejemplos de estas tecnologías son Autonomous Database y Microsoft Azure SQL.


**Metáfora:** Funcionan como un "administrador de bases de datos invisible" que vigila y ajusta el rendimiento del sistema de forma ininterrumpida las 24 horas, liberando a los profesionales técnicos de tareas repetitivas para que se enfoquen en la estrategia de la arquitectura de datos.
## NoSQL (Not Only SQL)
Representa una categoría de sistemas de gestión de bases de datos no relacionales desarrollados para abordar las limitaciones de las bases de datos relacionales tradicionales, especialmente en entornos modernos caracterizados por grandes volúmenes, alta velocidad y variedad de datos. Su diseño se caracteriza por no utilizar relaciones explícitas (claves primarias y foráneas), ofrecer un esquema flexible o dinámico (schema-less) y priorizar la escalabilidad horizontal y la disponibilidad.


**Ejemplo:** Bases de datos orientadas a documentos, sistemas clave-valor, bases de datos de grafos o de columnas anchas. Se aplican comúnmente en Big Data, redes sociales (como almacenamiento de perfiles de usuarios) e Internet de las Cosas (IoT).
## Escalabilidad horizontal
Es el método de escalado característico de las bases de datos NoSQL que consiste en distribuir la carga de trabajo y el almacenamiento de datos entre múltiples servidores o nodos en un clúster. Esto facilita la expansión elástica para manejar inmensos volúmenes de datos utilizando hardware de menor costo y sin introducir tiempos de inactividad o puntos únicos de fallo, a diferencia del escalado vertical (típico de SQL) que requiere añadir más hardware a un único servidor físico.


**Ejemplo:** Añadir tres servidores de menor coste a un clúster de base de datos NoSQL para soportar un pico de tráfico, en lugar de comprar un único servidor con un procesador extremadamente caro y limitado (lo que se conoce como escalabilidad vertical).
## Modelo BASE
Siglas en inglés de Basically Available, Soft state, Eventual consistency (Básicamente Disponible, Estado Flexible, Consistencia Eventual). Es el modelo de diseño y consistencia que adoptan las bases de datos NoSQL, priorizando la alta disponibilidad y la tolerancia a particiones del sistema sobre la consistencia inmediata y estricta de los datos (la cual se alcanza de manera diferida o eventual).


**Ejemplo:** Es el modelo en el que se apoyan la mayoría de las bases de datos NoSQL distribuidas para poder escalar de manera masiva a costa de no tener una actualización en tiempo real idéntica en cada réplica del servidor.
## Teorema CAP
Teorema que postula que un sistema de datos distribuido solo puede garantizar de manera simultánea dos de las siguientes tres propiedades: Consistencia, Disponibilidad y Tolerancia a particiones. En este marco, las bases de datos NoSQL suelen optar por la Disponibilidad y Tolerancia a Particiones (AP) sobre la Consistencia estricta (CA).


**Ejemplo:** Las bases de datos relacionales tradicionales (SQL) suelen priorizar la Consistencia y Disponibilidad (CA), mientras que los sistemas NoSQL distribuidos se diseñan bajo el enfoque de Disponibilidad y Tolerancia a particiones (AP).
## Persistencia políglota
Es la práctica arquitectónica de desarrollo de software que consiste en utilizar diferentes tipos de tecnologías de bases de datos (tanto relacionales como no relacionales) dentro de una misma aplicación o sistema de información, eligiendo la tecnología de persistencia de datos más óptima para cada tarea o problema específico.


**Ejemplo:** Un sistema de comercio electrónico que utiliza una base de datos relacional (SQL) para procesar transacciones de compras y facturación (asegurando consistencia), una base de datos NoSQL de grafos para el motor de recomendaciones de productos, y una base de datos clave-valor para gestionar las sesiones activas de los usuarios en la web.
**Metáfora:** Funciona como un artesano que utiliza diferentes herramientas diseñadas específicamente para cada tipo de material, en lugar de intentar solucionar todo con una sola.
## HTAP (Hybrid Transactional/Analytical Processing)
Procesamiento híbrido de transacciones y análisis en tiempo real que permite la generación, procesamiento, almacenamiento y consumo analítico de datos dentro de un único sistema integrado. Está diseñado para sincronizar millones de transacciones diarias mientras responde con rapidez a solicitudes analíticas complejas de Big Data en tiempo real, combinando funciones OLTP y OLAP.


**Ejemplo:** Un sistema comercial que registra y procesa millones de transacciones de ventas diarias y, de manera simultánea e inmediata, permite al equipo directivo ejecutar reportes analíticos complejos sobre el comportamiento del mercado en tiempo real.
**Metáfora:** Imagina una tienda que tradicionalmente tiene dos departamentos separados: uno para cobrar a los clientes (ventas) y otro para estudiar el mercado (análisis). HTAP es como un único departamento que hace ambas cosas al mismo tiempo y con la misma información al instante.
## NewSQL
Es una categoría emergente de bases de datos que busca combinar la escalabilidad horizontal y la flexibilidad de los sistemas NoSQL con las garantías ACID de consistencia estricta y la compatibilidad de consultas SQL del modelo relacional. Su objetivo es ofrecer alta velocidad y escalabilidad para aplicaciones modernas sin comprometer la integridad transaccional. Ejemplos destacados incluyen CockroachDB, Google Spanner y NuoDB.


**Ejemplo:** Su implementación es crítica en aplicaciones financieras de alta escala o sistemas de comercio electrónico globales que no pueden comprometer la integridad y consistencia de las transacciones monetarias.

## Metalenguaje
Un lenguaje que no se utiliza para programar acciones, sino para describir, definir o estructurar otros lenguajes o esquemas de datos.
**Ejemplo:** XML es un metalenguaje porque no realiza procesos lógicos, sino que sirve para que un usuario defina sus propias etiquetas y reglas estructurales para describir información.

## Interoperabilidad
La capacidad que tienen diferentes sistemas, entornos de software o hardware heterogéneos para comunicarse, intercambiar y utilizar información de manera efectiva gracias al uso de formatos y estándares comunes.
**Ejemplo:** El intercambio de datos entre sistemas desarrollados en diferentes lenguajes de programación mediante servicios web que utilizan XML o JSON como formato estándar de comunicación.

## Schema-less (Sin Esquema)
Propiedad de los sistemas de almacenamiento de datos que no imponen una estructura o esquema rígido y predefinido antes de poder guardar la información. Permite almacenar datos heterogéneos y realizar cambios de forma ágil.
**Ejemplo:** En una base de datos de documentos NoSQL, un registro de "usuario" puede tener únicamente los campos nombre y email, mientras que otro registro en la misma colección puede incluir además teléfono, dirección y un listado de preferencias sin alterar la base de datos.

## FAQ: ¿Cómo debe codificarse el carácter especial & para que el documento sea válido?
El carácter especial & debe codificarse escribiéndose como &amp;.

## FAQ: ¿Qué función cumple el DTD (Definición de Tipo de Documento) en relación a XML?
El DTD cumple la función de garantizar que los datos tengan la estructura correcta antes de ser procesados por una aplicación. Valida que el archivo XML esté construido de manera correcta, asegurando que respete las reglas definidas de estructura, orden, jerarquía y atributos.

## FAQ: ¿En qué parte del archivo se sitúa un DTD de tipo interno?
Un DTD interno se incluye dentro del mismo archivo XML, específicamente ubicado entre la declaración <!DOCTYPE ... [...]>.

## FAQ: ¿Qué palabra clave se utiliza en el XML para referenciar un archivo DTD externo?
Para referenciar un archivo DTD externo se utiliza la palabra clave SYSTEM.

## FAQ: ¿En qué tipo de servicios se utiliza XML para lograr la interoperabilidad empresarial?
XML se utiliza principalmente en servicios web (SOAP) y en la integración de aplicaciones empresariales (EAI).

## FAQ: Persistencia Políglota
Definición: La persistencia políglota es la práctica de utilizar diferentes tipos de bases de datos para satisfacer distintas necesidades de almacenamiento dentro de un mismo sistema, eligiendo la tecnología más adecuada para cada problema particular en lugar de utilizar un único tipo de base de datos para todo. Fin de la era monolítica: La base de datos monolítica quedó atrás porque las arquitecturas modernas necesitan integrar una combinación de tecnologías para optimizar cargas de trabajo específicas, creando así sistemas más escalables y adaptados a la necesidad de respuestas rápidas. Ejemplo: Una empresa que utiliza bases de datos relacionales (SQL) con estricta consistencia ACID para su sistema de transacciones bancarias, y al mismo tiempo emplea una base de datos NoSQL para manejar los perfiles y escalar masivamente su red social.

## FAQ: Complejidad técnica en la Migración de Datos
Desafíos y riesgos técnicos específicos asociados a la variedad de activos de datos y a la gestión de esquemas y diferencias. Variedad de activos de datos: La existencia de información en diferentes formatos, estructuras y ubicaciones aumenta la complejidad técnica, ya que los datos no estructurados carecen de un modelo predefinido y requieren ser indexados y organizados sistemáticamente en el sistema de destino. Gestión de esquemas y diferencias: El desafío radica en que incluso pequeñas discrepancias entre los almacenes de datos, como formatos de fecha distintos, pueden convertirse en problemas colosales si no se realizan las conversiones adecuadas al migrar.

## FAQ: Desafíos Operacionales en Entornos Distribuidos
Por qué los beneficios nativos de NoSQL se transforman al mismo tiempo en desafíos arquitectónicos complejos y habilidades requeridas. Transformación en desafíos: Beneficios como la flexibilidad del esquema y la distribución por diseño se vuelven desafíos operativos porque complican la gestión de los esquemas y las diferencias de la base de datos, mientras que la distribución inherente dificulta asegurar la consistencia de los datos y el manejo de transacciones distribuidas. Esto transfiere el cuello de botella desde las limitaciones de hardware hacia la gobernanza de datos. Habilidades requeridas: Las habilidades tradicionales de administración de bases de datos ya no alcanzan; se requiere que los profesionales tengan experiencia técnica enfocada en sistemas distribuidos, tuberías de datos, analítica y modelos de consistencia eventual.

## FAQ: Tecnologías Emergentes NewSQL
Objetivos y ventajas: NewSQL busca combinar la asombrosa escalabilidad horizontal masiva y flexibilidad de NoSQL, junto con las férreas garantías ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad) y la compatibilidad estricta de las bases de datos relacionales. El objetivo es proporcionar gran velocidad y escalabilidad sin comprometer la integridad transaccional de los datos. Herramientas: CockroachDB y Google Spanner.

## FAQ: Bases de Datos Autónomas y SDDP
En qué consisten: Las plataformas de bases de datos autónomas (SDDP) utilizan Inteligencia Artificial y algoritmos de Machine Learning para autogestionar el servidor, automatizando la creación de índices, la optimización de consultas, el parcheo de vulnerabilidades y el escalado de recursos físicos de forma completamente independiente. Modificación del rol del DBA: Al reducir la carga administrativa manual del servidor, el rol del Administrador de Bases de Datos (DBA) evoluciona; deja de ser un operador manual rutinario para convertirse en un estratega y arquitecto, centrando su trabajo en la gobernanza de los datos, la seguridad y la optimización de entornos complejos.

## FAQ: Integridad según Elmasri y Navathe
Según Elmasri y Navathe (2016), la integridad de datos es "la propiedad que garantiza la corrección y validez de los datos en la base de datos, asegurando que cumplan con restricciones predefinidas y evitando inconsistencias".

## FAQ: Tres tipos de restricciones de integridad y ejemplos SQL
Integridad de entidad: Garantiza que cada registro de una tabla sea único y no nulo mediante el uso de claves primarias. Ejemplo SQL: id_cliente INT PRIMARY KEY.
Integridad referencial: Mantiene relaciones coherentes y válidas entre tablas, asegurando que un valor de referencia en una tabla exista en la otra. Ejemplo SQL: FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente).
Integridad de dominio: Controla que los valores asignados a una columna cumplan con condiciones lógicas, de nulidad o de unicidad. Ejemplo SQL: total DECIMAL(10,2) CHECK (total > 0).

## FAQ: Definición de Bloqueo y sus tipos
Un bloqueo es una restricción temporal que aplica el sistema de gestión de bases de datos (SGBD) para evitar que dos o más transacciones accedan o modifiquen el mismo dato al mismo tiempo, garantizando así la coherencia de la información. Tipos: Bloqueo Compartido (Shared Lock - S Lock): Se activa cuando una transacción solo va a leer un dato. Varias transacciones pueden leer el mismo dato a la vez, pero ninguna de ellas lo podrá modificar hasta que todos los bloqueos compartidos se liberen. Bloqueo Exclusivo (Exclusive Lock - X Lock): Se aplica cuando una transacción modifica un dato. Mientras esté activo, ninguna otra transacción puede leer ni modificar dicho dato.

## FAQ: Identificación de tipos de integridad (Práctico)
Basándonos en tablas Clientes y Pedidos:
Los id_cliente existen en la tabla Clientes: Integridad Referencial. Justificación: Se define mediante clave foránea (FOREIGN KEY), lo que impide ingresar pedidos referenciados a un cliente inexistente.
total es > que 0: Integridad de Dominio. Justificación: Se controla mediante CHECK (total > 0).
email es único: Integridad de Dominio. Justificación: Se define mediante UNIQUE, restringe duplicados.
id_cliente y id_pedido son únicos: Integridad de Entidad. Justificación: Se implementa declarando cada campo como PRIMARY KEY en su respectiva tabla.

## FAQ: Escenario práctico de bloqueos (Actualización y Lectura Concurrente)
Cuando un usuario actualiza el saldo de una cuenta y otro usuario intenta leerlo simultáneamente sin bloqueos aplicados podría ocurrir Lectura sucia (Dirty Read). El segundo usuario leería un dato transitorio que posteriormente podría descartarse (ROLLBACK). Se debe aplicar un Bloqueo Exclusivo (Exclusive Lock / X Lock) sobre la fila a modificar (con FOR UPDATE), impidiendo cualquier lectura o modificación concurrente hasta confirmar la transacción. Ejemplo SQL:
START TRANSACTION;
SELECT saldo FROM Cuentas WHERE id_cuenta = 1 FOR UPDATE;
UPDATE Cuentas SET saldo = saldo - 100 WHERE id_cuenta = 1;
COMMIT;
