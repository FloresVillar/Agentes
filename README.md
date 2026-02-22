# USO DE AGENTES

**La infraestructura del proyecto** 

```bash
________________________________________________________________________
|                                                                        |
|   HOST (Tu Computadora / Servidor)                                     |
|    ________________________________________________________________    |
|   |                                                                |   |
|   |   RED VIRTUAL (agent-network)                                  |   |
|   |   [ Permite que los contenedores se hablen por su nombre ]     |   |
|   |    __________________________        __________________________|   |
|   |   |                          |      |                          |   |
|   |   |  CONTENEDOR:             |      |  CONTENEDOR:             |   |
|   |   |  agente-python           |      |  ollama-server           |   |
|   |   |__________________________|      |__________________________|   |
|   |   |                          |      |                          |   |
|   |   |   SERVICIO (app):        |      |   SERVICIO (ollama):     |   |
|   |   |   > Código Python        | <==> |   > Servidor Ollama      |   |
|   |   |   > Entorno:             | (API)|   > Puerto: 11434        |   |
|   |   |     OLLAMA_HOST          |      |                          |   |
|   |   |__________________________|      |__________________________|   |
|   |                ^                    |            |             |   |
|   |________________|____________________|____________|_____________|   |
|                    |                                 |                 |
|      PUERTO 11434  |               VOLUMEN EXTERNO   |                 |
|      (Acceso desde |               (ollama-data)     |                 |
|       tu navegador)|               [ Guarda los      |                 |
|             ^      |                 Modelos LLM ] <—/                 |
|             \______/                                                   |
|________________________________________________________________________|
Cortesia de Gemini
```

**La arquitectura**

<p align=center>
    <img src=imagenes/arquitectura.png width="80%">
</p>
    
**Ejecucion**
 
```bash
    python -m venv venv_agentes
    .\venv_agentes\Scripts\activate
    # ejecutando el .ps1 analogo a Makefile
    .\run_docker.ps1 build    # construccion de imagenes
    .\run_docker.ps1 run      # levantando contenedores  e instalacion del modelo
    .\run_docker shell-app    #dentro de agente-python
    python -m main app.main    
    #input recomendado
    consulta empresa X
```
Ahora se detalla la teoria implementada

**Resumen amablemente sintetizado por chatgpt**

Un agente es un SISTEMA que 
- Recibe informacion 
- Razona
- Toma desiciones
- Usa herramientas

No unicamente responde texto tambien ejecuta
```bash
Un LLM norml :  
    recibe entrada → otorga una salida
```

```bash
Un agente:
    Entrada → Plan → Decision → Usando las herramientas → Observa Resultado → Ajusta → Salidas finales

```
Es un agente propiamente! 

## RAG

Retrievel-Augmented Generation

Que se aborda ? un llm no accede a nuestros datos , no conoce informacion privada.

RAG = recuperar informacion + generar respuesta

```bash
    → Pregunta 
    → Busca en la base de datos 
    → Recuperar documentos relevantes 
    → inyecta en el prompt 
    → Generar respuesta


```

Sus componenetes tecnicos : 
- Embedding 
- Vector databases
- similaridad coseno
- chunking  
- context window

Sus ventajas 
- Reduce alucinaciones (ahora el agentes es un llm que accede a la data) al fundamentar la generacion en informacion recuperada externamente

- No necesita fine-tunning

RAG y fine-tunnig se complementan...Bueno beuno,se ha de profundizar en esta ultima frase . <br>

## RAG Vs Fine-tunning

RAG no modifica el modelo , el modelo tiene los mismos W y b (entiendo).

Mientras que **Un LLM modela P(y | x)** x=prompt ,  y=respuesta. 

Lo que RAG lo que hace es **P( y | x + d)** 

d = documentos recuperados dinamicamente
```bash
    P(y | x)       x=prompt
    P(y | x + d )  d =documentos accedidos

    El modelo sigue siendo P theta , theta :parametros del modelo
```
El modelo es el mismo, lo que cambia es el contexto. De modo que no hay actualizacion de pesos, ni entrenamiento adicional , no se modifica el comportamiento del modelo

FINE-TUNNING  si cambia el modelo, tomamos los W y los actualizamos **W'  = W - contante * gradiente**

```bash
    W′ = W −η ∇L
    L = funcion de perdida
```
De tal forma que se cambia el como razona,(no en un sentido estricto sino que ajustamos la distribucion P theta para que favorezca ciertos patrones) como responde, el estilo , estructura de salida...

**disclaimer** 
```bash
    Fine-tunnig:
    θ′=θ−η∇θ​L
    # cambia la distribucion de salida
    EJEMPLO :
    P theta ("Si, señor "| x ) = 0.15
    luego
    P theta ("Si, señor" | x)  = 0.72

    Regularizacion:
    L′=L+λR(θ)
    # se agrega un termino a la funcion coste/perdida , evitando el sobreajuste, restringimos cuanto se mueven los parametros

    RLHF 
    L=Lreward ​+ β KL(Pθ​ ∣∣ Pbase​)
    # ajustamos theta para que la distribucion refleje preferencias humanas
    KL actua como regularizacion 
```


Entonces RAG modifica conocimiento accesible . <br>
Fine - tunning modifica comportamiento aprendido

Los ejemplos siguientes son tanto intuitivos y refuerzan los conceptos:

- Se necesita que el modelo conozca leyes actualizadas: 
    
    Indexamos documentos legales

    Recuperamos lo relevante
    
    Inyectar esto en el contexto

- Se necesita que el modelo responde siempre en formato json. 

    RAG no ayuda, esto no es un problema de conocimiento

    Es comportamiento

## MCP 
Model Context  Protocol

Propuesto por Anthropic, es un protocolo de comunicacion entre un LLM y las herramientas externas

Un poco de historia : antes cada empresa se conectaba a los LLM de forma distinta, una api para base de datos, otra forma para archivos, etc . Obteniendose integraciones fragiles, sin estandar y dificil interoperabilidad.

MCP es una abstraccion que define : 
- como se describe herramientas
- como el modelo lo usa
- como se devuelve el resultado
- como gestionamos memoria y contexto

Vamos que, es un protocolo como tal (como http sql) 

```bash
sitema tradicional
 Usuario → llm → texto
```
Con MCP 

```bash        solicitud
    usuario →   llm  →  MCP server → Tool/api/db → respuesta → llm → final
```

Modelo matematico:
```bash
# LLM tradicional
P( yt | x,y < t )

- PREGUNTA ¿cual es la capital de peru ?

x = contexto 
y < t = tokens previos

#sin herramientas  se hacia  

y = arg maxP(y|x)

#Dado este texto de entrada, que respuesta es mas probable
    argmax ..
    y       |        P(y)
    -------------------
    A                  0.1
    B                  0.7
    C                  0.2
        arg max P(y) = B

- RESPUESTA 
    Lima

```
Detalle matematico de como se genera token por token

```bash
    P(y | x ) = ∏ P(yt ​∣ x,y<t​)    i:1→n
    La probabilidad total de la respuesta es el producto de las probabilidades de cada token condicionado a los anteriores
    Si la respuesta es Lima es la capital
    el modelo calcula :
        - P("lima" | x)
    
        - P("es" | x, "Lima")

        - P("la" | x, "Lima es")
        ....
    En la practica no se usa argmax puro , sino sampling, ,temperature, top-k ,p 
```
Otro detalle matematico y de notacion
```bash
Un LLm es una funcion parametrizada 
P theta( y | x) = f theta (x)   f theta : x → Δ∣V∣  

P = distribucion de probabilidad 
Theta = parametros del modelo 
x = input 
y = output
f theta = red neuronal (transformer) , devuelve una distribucion sobre el siguiente tokens
V = vocabulario
Δ∣V∣  = simplex de probabilidad

EJEMPLO:
    ["Lima","Cusco","Arequipa"]
    token               probabilidad
    lima                0.85
    cusco               0.10
    arequipa            0.05

    Esto es P theta(y | x)
    luego al hacer
    **argmaxP(y | x)**
    Se elige el "token" de mayor probabilidad


```

```bash
# AGENTES
    1. Generar texto 
    2. Emitir una llamada estructurada a herramienta

    ## el modelo no solo genera texto sino una accion
    ejemplo ..
    - PREGUNTA : ¿cuantos empleados tiene la empresa X ?
    

    accion t E {text, tool1, tool2, ...} 
    
    - ACCION  
    {
        "tool_call": "consultar_empresa",
        "params": {
        "nombre": "Empresa X"
        }
    }

    El modelo aprende
    P(accion t | x, historia t -1)  ~ P(respuesta | prompt)
    
    SI : 
    
    accion t = argmax P (accion | x, h t-1) = tool i      # como en el ejemplo

    o = MCP . execute Ti(params) =  E(Ti, params) # resultado de ejecutar la herramienta ,# el output resultado de ejecutar la herramienta Ti con ciertos parametros, Ti : T1 =  buscar_documentos, T2 = consultar_based ,T 3 = ejecutar_Codigo ; params  { "query" : "Contrato laboral peru 2025"}, E es el entorno de ejecucion estandaizado por MCP
    - OUTPUT 
    o = T consultar_empresa ({"nombre":"Empresa X"})
    - ACTUALIZACION 
        h t = h t-1 + accion t   +  ot # hasta que la accion es responder ?
        el modelo vuelve a cacular P theta (accion t+1 | ht)  ~despues~ P theta(y | ht) # IR a ACCION

    SI :
     accion t = Respuesta_final
     el modelo genera
         y ~ P theta(y | h t-1)
    - SALIDA FINAL

    { "Empleados" : 523}
    
```
 
Resumen de gemini:
1. LLM tradicional

Una funcion de un solo paso,  el proceso es lineal , el modelo intenta predecir el token mas probable:

- Ecuacion y  = argmaxP(y | x)
- El modelo confia en sus pesos W , su mision es maximizar la probabilidad del siguiente texto

2. Agente, bucle iterativo

El argmax ocurre multiples veces , es un ciclo de pensamiento. El proceso matematico :
- Decide accion P(at | x,ht-1) esto es cual es la accion **a** mas probable dado el prompt x y el historial h.

- si **at** es una herramienta (SQL) se ejecuta externamente y obtiebe una obsevacion **ot** 

- Actualizacion del contexto , el nuevo prompt  **x' = x + at + ot**

- Respuesta final ,cuando el modelo predice que la mejor accion es "Responder al usario" genera **y** final

Finalmente, en el LLM tradicional ,el argmax genera contenido . En tanto que en el agente, el argmax genera primero instrucciones de control (llama a la API) y luego de ello genera el contenido.

 
## Descripcion de la "infraestructura"

Como inicio se define el arbol de directorios,segun la practica recomendada y siguiendo las practicas de diseño 
```bash
.
├── app
│   ├── agente.py
│   ├── __init__.py
│   ├── llm.py
│   ├── main.py
│   ├── mcp.py
│   ├── memory
│   ├── __pycache__
│   ├── schemas
│   └── tools
        ├── empresa.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── README.md
├── requirements.txt
├── run_docker.ps1
├── run_local.ps1
├── tests
└── venv_agentes

```
Se dispondran de dos servicios **app**  y **ollama** ambos dentro de contenedores levantado en base a imagenes Docker.

 Para el **services** con etiqueta **app** , construye su imagen mediante la instruccion **build** quien establece su contexto en la carpeta actual **.** de modo que buscara en la carpeta actual el **Dockerfile** 

 La directiva **volumes: - ./app:/app/app**  permite montar el codigo local dentro del contenedor , lo cual nos permitirá modificar scripts sin reconstruir la imagen, esto no toca los volumenes de produccion (ollama),unicamente exponemos el codigo local al contenedor.
Montamos todo lo que hay dentro de /app de nuestro host en /app del contenedor, luego al ejecutar **python -m app.main** python busca un paquete app dentro de /app (WOKDIR /app) ,pero al no haber un directorio app dentro de /app , lo que hace es declarar esa estructura de carpetas en volumes  como /app/app


 Se establece la relacion de orden  (mas no de disponibilidad)  mediante **depends_on: - ollama:** por lo que se recomienda usar un **healthcheck** de modo que Docker correra esta prueba cada ciertos segundos. en services **ollama: condition: service_healthy** y en ollama **healthcheck: test** .

Seguidamente las variables de entorno que python recibira **environment:** **OLLAMA_HOST =** que Docker resolvera automaticamente.

**networks** declara la red para los contenedores (estado deseado) , recordar que el .yml describe el estado deseado que Docker se encargara de construir.

En tanto que las sentencias **stdin_open: true** y **tty: true** mantienen el contenedor interactivo


Para el service **ollama** usamos una imagen disponible en DockerHub , mapeamos los puertos **host:contenedor** , de esta forma el usario se comunica desde su maquina con el contenedor.
Seguidamente con sentencia **volumes** Docker guardara los modelos descargados  en el volumen **ollama-data** ,de tal forma que si se borra el contenedor, lo descargado persiste.

Finalmente las clausuras del contrato , las declaraciones globales **volumes y networks** dan permiso a Docker para crear un objeto de almacenamiento independiente , de modo que Docker gestiona una area en disco sin que se tenga que crear una carpeta para guardar el modelo. Este es el volumen persistente del que hablamos antes. 

Asimismo **networks** crea una red privada tipo bridge(por defecto). El DNS interno de esta red permite que python use http://ollama y asigne ip para esta red.



## Descripcion de la arquitectura

Una vez declarado la insfraestructura, veamos que arquitectura sustenta el proceso congnitivo.

Debido al este nivel casi introductoria , se implementara la teoria de agentes casi tal cual, esto es como un proceso de desicion secuencial.
### Agentes.py

En **Agentes.py** Se calcula la accion mas probable **a_t = llamada_a_modelo** quien implementa la distribucion de probabilidad de las acciones probables dado el promp y el historial **at = argmax Ptheta(a | x,ht-1)**

La acccion a_t **{"herramienta_llamada":"consultar_empresa", "parametros":{"nombre":"Empresa X"}}** .  

Ahora con la accion obtenida , ejecutamos la herramienta con los parametros de la accion , esto es la parte practica de **o = MCP . execute Ti(params) =  E(Ti, params)**, se usara un mcp ficticio , sin embargo cabe señalar que este protocolo para la obtencion de output en base a herramientas es mas potente.


Finalmente actualizamos el historial **h_t+1 = h_T  + a_t  +  o_t** , los h_t.append respetan el estandar de la API de OpenAI, debido a que esta espera que los mensajes tengan un "contrato" especifico, en este caso diccionarios donde las claves son rol y content.


La salida de la iteracion se da cuando a_t no contiene la clave **herramienta_llamada** esto es que ya se obtuvo a respuesta final

### llm.py
En este script vive el modelo ollama , tambien provisto por openai, si bien es cierto que existen modelos mejores , con cientos de millones de parametros (W y b) , por un tema de limitaciones de memoria se usara el modelo llama3.2 , uno muy liviano.

Se crea el cliente **cliente = OpenAI()** con una variable de entorno por defecto **OLLAMA_HOST** .

La funcion **llamada_a_modelo** invocada desde agentes.py concatena el historial de **mensajes** , haciendo luego la consulta al modelo con ese mensaje como argumento **cliente.chat.completions.create(..message=mensajes..)**

### mcp.py

Donde se definen los tools como pares clave-valor. La funcion **ejecutar_herramienta** invocada desde agentes ejecutan a su vez una llamada a por ejemplo **consultar_empresa** del modulo tool/empresa.py mediante **return TOOLS(nombre)(parametros)**

### tools/empresa.py

Las funciones consultar_empresa reciben el nombre como argumento y devuelven la informacion **return {"empleados":mock.get(nombre,"No hallado")}**

### main.py

Finalmente  el script que inicia la ejecucion , dentro de un bucle se recibe la entrada de usuario y se hace la llamada al agente via **iniciar_agente** , esto sera ejecutado (eso se pretende) dentro del contenedor que correra la linea CMD ["python","-m","app.main"]

La imagen de elaboracion propia corresponde a la arquitectura minimalista del proyecto (ver imagen de arquitectura al inicio)



 