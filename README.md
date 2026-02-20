# USO DE AGENTES
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



# Parte practica

Como inicio se define el arbol de directorios,segun la practica recomendada y siguiendo las practicas 
Entorno vitual
```bash
    python -m venv venv_agentes
    .\venv_agentes\Scripts\activate
```
Instalando anthropic

```bash
    pip install anthropic
```
