Una vez detalla la arquitectura, descrito de manera detallada en funcionamiento de todos scripts e implementada la teoria matematica; testearemos dentro del contenedor 
**agente-python** 

Merced al volumen montado en el service **python** que permite que el contenedor **agente-python** tome las modificaciones de nuestros scripts
```bash
    # ingresando al contenedor
    docker exec -it agente-python /bin/bash
    # una vez dentro ejecutamos main
    root@36b32f6eb10f:/app# python -m app.main
    
    # vemos que indudablemente ALUCINA demasiado

    - Usuario: TEXTO ARBITRARIO
    Respuesta final:"Herramienta llamada consultar_empresa, parámetros{'.nombre': 'Empresa Y'}"

    
    - Usuario: texto

    output del entorno: {'empleados': 100}
    Respuesta final:No, esa no es una respuesta en JSON. En lugar de eso, te proporcionaré un ejemplo de respuestas en formato JSON:
    {
        "empleados": 90,
        "direccion": "Av. Colina S/N",
        "telefono": "0900-1234567"
    }
    Este es un JSON que contiene información sobre una empresa con dos campo: `empleados` y `direccion`.


    - Usuario:de nuevo

Respuesta final:Como estás buscando que te dé información en formato JSON, puedo ayudarte a crear un respaldo de cómo sería la respuesta correcta:

{
  "herramienta_llamada": "consultar_empresa",
  "parametros": {
    "nombre": "Empresa X"
  }
}

Si necesitas la respuesta al usuario, estoy listo para ayudarte con eso. ¿Necesito que te diga cómo hacer qué?


- 
```

Conviene precisar que de momento se ha construido un agente con herramientas, se intenta hacer funcional el codigo antes de implementar RAG. 

Señalar en primer lugar que el modelo tiene 1B de parametros,es uno muy pequeño, por lo tanto el PROMPT tiene que ser minimalista y lo mas conciso posible.

Ademas una precision conceptual, si bien es cierto se tiene un prompt detallado en : [system: PROMT] [user:input]  ver  **llm.py** , este PROMT no define la consulta sino las reglas del agente, entonces el **input** tiene que ser tambien puntual.

Para ver el flujo y tener una idea clara de como h_t va creciendo, de como  **message** es formado para ser el argumento del modelo, se disponde del siguiente ejemplo

llm.py recibe el prompt y el historial como argumentos, **mensajes = [{"role":"system","content":prompt}] + h_t** 
 
Algunos detalles, ollama es un Servidor Web Local ,al correrlo queda escuchando en el puerto 11434(tambien en el contenedor). entonces la llamada http envia un paquete de datos por la red interna Docker(en este caso) a **http://ollama:11434/v1/chat/completions**

Entonces lo que se envia a este servidor via cliente... es 
```bash
    {
        "model": "llama3.2:1b",
        "messages":[
            {"role":"system","content":"PROMPT} 
            
            {"role":"user", "content":"content"}
            ],
        "max_tokens": 300,
        "temperatura": 0
    }
```
Sin embargo el modelo los serializa 
```bash
<|system|>
PROMPT

<|user|>
input

<|assistant|>
```
Y los tokeniza, [128000,345,9981,..] y esto es con lo que trabaja el transformer. Prediciendo los siguientes tokens dado los anteriores.

Con esas consideraciones el PROMPT = ""Solo JSON 

Herramienta:
{"herramienta_llamada":"..","":{}}
Respuesta:
{"respuesta":"texto"}
""

Y en input de usuario **consulta empresa X** , de tal forma que se abarca la **accion deseada**, **el objeto de esa accion** y **la entidad concreta** . Entonces P(a_t | system , input) construido por el modelo no es amplia, cosa que seria si el input fuera debil. 

Otra detalle es que debido a lo pequeño del modelo,es esquema OpenAi moderno no se dispone del todo, **tool** no se dispone como rol.

Con esto implementado 
 ```bash
    docker exec -it agente-python /bin/bash
    python -m app.main

    ```
Usuario:consulta empresa X
output del entorno: {'empleados': 100}

output del entorno: {'empleados': 100}

Respuesta final:Lo siento, parece que la respuesta ya se obtuvo anteriormente. Si deseas obtener una nueva respuesta, necesitarías reemplazar el parámetro "nombre" con un nuevo valor..
 ```

Para evitar que la consulta se recalcule
**at+1​=herramienta otra vez** se introduce una bandera ya_ejecuto  = False, y cuando se ejecute se cambia a True, de tal forma que **and not ya_ejecuto** sera falso y no ejecuta el bloque.

```bash
(venv_agentes) (base) PS G:\Esau\2025_3\agentes> docker exec -it agente-python /bin/bash
root@36b32f6eb10f:/app# python -m app.main
Usuario:consulta empresa X
output del entorno: {'empleados': 100}

Respuesta final:{"herramienta_llamada":"consultar_empresa","parametros":{"nombre":"Empresa X"},"respuesta": "El número de empleados de la empresa X es 100."}
Usuario:consulta empresa Y
output del entorno: {'empleados': 200}

Respuesta final:{"herramienta_llamada":"consultar_empresa","parametros":{"nombre":"Empresa Y"},"respuesta": "Los empleados de la empresa Y son 200" }
Usuario:consulta empresa Z
output del entorno: {'empleados': 'No hallado'}

Respuesta final:Lo siento, pero parece que hubo un error en la respuesta. El resultado es un objeto con dos propiedades: "empleados" y "No hallado", lo que indica que no se encontraron empleados para la empresa Z.

Si deseas obtener una respuesta diferente, como un texto o un número, debes especificar qué tipo de respuesta deseas obtener. Por ejemplo:

{"herramienta_llamada":"consultar_empresa","parametros":{"nombre":"Empresa Z"},"respuesta":"El número de empleados es 1000."}
Usuario:
```

Consiguiendo los objetivos deseados, siempre en el contexto de un modelo muy ligero.

La depuracion (aunque suene pretensioso) se realiza merced de los comandos docker:
```bash
    docker compose up -d #encendemos los motores , se construye el contenedor , mo si ya existiera -d se encarga de ello
```
Luego hecho los cambios en los scripts **docker exec -it agente-python /bin/bash** es un nuevo proceso que lee el archivo desde disco (ya con los cambios), pero el servidor podria estar usando funciones  un proceso anterior que estan en la RAM, luego la API seguria respindiendo con la logica anterior , para evitar esto se usa
```bash 
docker compose restart app
```
Una vez dentro del contenedor , se realiza la consulta 
```bash
root@36b32f6eb10f:/app# python -m app.main
Usuario:consulta empresa Y
output del entorno: {'empleados': 200}

Respuesta final:{"herramienta_llamada":"consultar_empresa","parametros":{"nombre":"Empresa Y"},"respuesta": "Los empleados de la empresa Y son 200" }
Usuario:salir
Terminando
```