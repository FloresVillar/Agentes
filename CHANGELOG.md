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

Okay , pero en este punto se usa un mock, no una data real; es mas, el mcp.py actual no es el estandar MCP, ni mucho menos.A lo sumo, se dispone de un React Loop (razonamiento + accion) de modo que para implementar el MCP, de modo que agente no llamara solo a funciones sin a un servidor MCP con recursos y herramientas

<p align=center>
    <img src="imagenes/arquitectura_2.png" width="80%">
</p>

**tools/empresa.py→mcp_server.py**

Tools/empresa.py debera ser reemplazado por un/unos servidores.

Lo reemplazamos por server_mcp.py , donde se crea un objeto FastMCP agregando a su catologo de funciones las funciones **consultar_empresa** y **buscar_documentos** mediante el decorador @mcp.tools

```bash
from mcp.server.fastmcp import FastMCP

# Creamos el servidor
mcp = FastMCP("Servidor-Empresarial")

@mcp.tool()
def consultar_empresa(nombre: str) -> str:
    """Consulta el número de empleados de una empresa."""
    mock = {"Empresa X": 100, "Empresa Y": 200}
    return f"Resultado: {nombre} tiene {mock.get(nombre, '0')} empleados."

@mcp.tool()
def buscar_documentos(nombre_documento: str) -> str:
    """Busca documentos específicos en la base de datos."""
    return f"Documento '{nombre_documento}' ENCONTRADO."

if __name__ == "__main__":
    mcp.run()
```
**mcp.py**

El modulo mcp.py ya no tendra un simple array de diccionarios TOOLS, ahora se gestiona la comunicacion via stdio (estandar de MCP) . **server_params** configura el servidor como un subproceso con **args = ["-m","app.server_mcp"]""** .

En tanto que async de la libreria **asyncio** permite que la funcion pueda ser pausada , pues el unico worker gestionara la ejecucion concurrente de varias funciones. La conexion mencionada se establece merced a **stdio_client (server_params)** . Este objeto es usado dentro de las dos funciones **obtener_herramientas y ejecutar_herramienta**. La sintaxis aun no se profundiza a totalidad.


```bash
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuración para lanzar el servidor como un subproceso
server_params = StdioServerParameters(
    command="python",
    args=["-m", "app.server_mcp"], # Ejecuta tu servidor
    env=None
)

async def obtener_herramientas_mcp():
    """Descubre qué herramientas ofrece el servidor"""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.list_tools()

async def ejecutar_herramienta_mcp(nombre, parametros):
    """Llama a una herramienta siguiendo el protocolo real"""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            resultado = await session.call_tool(nombre, arguments=parametros)
            # El protocolo devuelve un objeto; extraemos el texto
            return resultado.content[0].text
```

**agente.py**

La funcion principal invocada desde **main.py** tambien se define como una CORRUTINA , de modo que puede pausarse, esto es que no devolvera la ejecucion de la funcion sino una promesa de que se ejecutará. Y desde luego el punto de pausa **await** que permite liberar el control del procesador, mientras este programa se ejecuta (calcula algo), se puede hacer otras tareas. Con **Event Loop** como orquestador de las corrutinas.Cuando una tarea usa await el Event Loop la pone en espera y salta a la siguiente tarea, **asyncio.run(main())** es el comando que enciende este motor.

```bash
import json
from .mcp import MCPManager
from .llm import llamada_a_modelo

async def iniciar_agente(input_usuario):
    manager = MCPManager()
    try:
        # 1. Handshake inicial: Descubrimiento de herramientas
        tools_disponibles = await manager.conectar_todos()
        
        # Inyectamos descripciones automáticamente en el System Prompt
        desc_tools = "\n".join([f"- {t.name}: {t.description}" for t in tools_disponibles])

        prompt_mcp = f"""
        Eres un agente que usa herramientas via MCP.
        Responde SIEMPRE en formato JSON.
        
        Herramientas que tienes instaladas:
        {desc_tools}

        Si necesitas una herramienta: {{"herramienta_llamada": "nombre", "parametros": {{...}}}}
        Si es respuesta final: {{"respuesta": "texto"}}
        """

        h_t = [{"role": "user", "content": input_usuario}]
        
        while True:
            # El LLM decide qué hacer
            a_t = llamada_a_modelo(h_t, prompt_mcp)
            a_t = a_t.strip().replace("```json", "").replace("```", "")

            try:
                a_t_ = json.loads(a_t)
                
                if "herramienta_llamada" in a_t_:
                    # El Manager busca en qué servidor vive esa herramienta y la ejecuta
                    o_t = await manager.ejecutar_en_cualquiera(
                        a_t_["herramienta_llamada"], 
                        a_t_["parametros"]
                    )
                    
                    h_t.append({"role": "assistant", "content": a_t})
                    h_t.append({"role": "user", "content": f"Resultado de herramienta: {o_t}"})
                    continue
                    
                return a_t_.get("respuesta", a_t)

            except json.JSONDecodeError:
                return a_t
    finally:
        # Importante: Cerramos todos los subprocesos de los servidores
        await manager.cerrar()
```

**main.py**

Tambien usamos corrutinas y puntos de pausa dentro de este modulo.

```bash
import asyncio
from .agente import iniciar_agente

async def main():
    print("Agente MCP Multiserver Activo (Escribe 'salir' para terminar)")
    while True:
        user_input = input("\nUsuario: ")
        if user_input.lower() in ["exit", "salir"]: break
        
        respuesta = await iniciar_agente(user_input)
        print(f"Agente: {respuesta}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

Sin embargo se tiene un escenario local , ahora se buscaria conectarse con servidores externos


<p align="center">
    <img src="imagenes/arquitectura.png" width="80%">
</p>

Los siguientes bloques de codigo no estan depurados, solo son sugerencias hechas por gemini

**mcp.py**

```bash
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LISTA DE SERVIDORES (Configuración centralizada)
servidores_a_conectar = [
    StdioServerParameters(
    command="npx", # Usamos Node.js para ejecutar el servidor oficial
    args=[
        "-y", "@modelcontextprotocol/server-postgres", 
        "postgresql://usuario:password@localhost:5432/mi_base_de_datos"
    ],
    env=None
),
    StdioServerParameters(
        command="npx", 
        args=["-y", "@modelcontextprotocol/server-filesystem", "G:/MisDocumentos"]
    ),
    StdioServerParameters(
        command="npx", 
        args=["-y", "@modelcontextprotocol/server-google-maps"], 
        env={"GOOGLE_MAPS_API_KEY": "AIza..."}
    ),
    StdioServerParameters(
        command="python", 
        args=["-m", "app.server_mcp"]
    ),
    # Tu nuevo servidor RAG
    StdioServerParameters(
        command="python", 
        args=["-m", "app.server_rag"]
    )
]

async def obtener_herramientas_mcp():
    """Descubre herramientas de TODOS los servidores configurados"""
    todas_las_tools = []
    for params in servidores_a_conectar:
        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    lista = await session.list_tools()
                    todas_las_tools.extend(lista.tools)
        except Exception as e:
            print(f"Error conectando a un servidor MCP: {e}")
    
    # Retornamos un objeto con atributo .tools para mantener compatibilidad con agente.py
    class ToolsWrapper:
        def __init__(self, tools): self.tools = tools
    return ToolsWrapper(todas_las_tools)

async def ejecutar_herramienta_mcp(nombre, parametros):
    """Busca y ejecuta la herramienta en el servidor que la contenga"""
    for params in servidores_a_conectar:
        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    # Verificamos si este servidor tiene la herramienta
                    tools_del_server = await session.list_tools()
                    if any(t.name == nombre for t in tools_del_server.tools):
                        resultado = await session.call_tool(nombre, arguments=parametros)
                        return resultado.content[0].text
        except Exception:
            continue
    return f"Error: La herramienta {nombre} no se encontró en ningún servidor."
```

**agente.py**

```bash
import json
import asyncio
from .llm import llamada_a_modelo
from .mcp import ejecutar_herramienta_mcp, obtener_herramientas_mcp

async def iniciar_agente(input_usuario):
    # 1. Descubrimiento dinámico (Handshake MCP)
    tools_disponibles = await obtener_herramientas_mcp()
    
    desc_tools = "\n".join([f"- {t.name}: {t.description}" for t in tools_disponibles.tools])

    # Opcional: Podrías llamar a 'recuperar_contexto' aquí antes del prompt para inyectar RAG
    prompt_mcp = f"""
    Solo responde en JSON.
    Herramientas disponibles:
    {desc_tools}

    Si necesitas una herramienta, responde: 
    {{"herramienta_llamada": "nombre", "parametros": {{...}}}}
    Si tienes la respuesta final:
    {{"respuesta": "texto"}}
    """

    h_t = [{"role": "user", "content": input_usuario}]
    
    while True:
        a_t = llamada_a_modelo(h_t, prompt_mcp)
        a_t = a_t.strip().replace("```json", "").replace("```", "")

        try:
            a_t_ = json.loads(a_t)
            
            if "herramienta_llamada" in a_t_:
                o_t = await ejecutar_herramienta_mcp(
                    a_t_["herramienta_llamada"], 
                    a_t_["parametros"]
                )
                print(f"MCP Output: {o_t}")
                
                h_t.append({"role": "assistant", "content": a_t})
                h_t.append({"role": "user", "content": f"Resultado: {o_t}"})
                continue 
                
            return a_t_.get("respuesta", a_t)

        except json.JSONDecodeError:
            return a_t
```

**llm.py**

```bash
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
cliente = OpenAI(api_key="ollama", base_url=os.getenv("OLLAMA_HOST")+"/v1")

def llamada_a_modelo(historial, prompt): 
    mensajes = [{"role": "system", "content": prompt}] + historial
    accion = cliente.chat.completions.create(
        model="llama3.2:1b",
        messages=mensajes,
        max_tokens=300,
        temperature=0
    )
    return accion.choices[0].message.content
```

**main.py**
```bash
import asyncio
from app.agente import iniciar_agente

async def main():
    print("Agente MCP iniciado. Escribe 'salir' para terminar.")
    while True:
        usuario = input("\ > ")
        if usuario.lower() in ["salir", "exit"]: break
        
        respuesta = await iniciar_agente(usuario)
        print(f"\n> {respuesta}")

if __name__ == "__main__":
    asyncio.run(main())
```

**RAG**
Implementado todo el potencial de MCP ahora se implementara Retrieval-Augmented Generation. 

El patron arquitectonico se formaliza mediante **a_t ~ P(a_t | ht , ct)**

ht = historial<br>
ct = contexto recuperada de una base de datos

Se definiran 
- Una base de datos vectorial
- Calculo de embeddings
- busqueda por similitud
- insercion de los documentos recuperados antes de llamar al modelo

```bash
docs = buscar_similares(consulta)
prompt = construir_prompt(docs, consulta)
respuesta = modelo(prompt)
```
**Embeddings**
Es una funcion que convierte un texto en un vector. En este espacio vectorial ,las palabras con significados similares estan geometricamente mas cerca.

- Si buscamos que el modelo entienda la relacion entre perro y cachorro
- Si se busca "problemas financieros"  el embeddings permite que el sistema encuentre documentos quee hablen de "quiebra" o "falta de liquidez" aunque no mencionen financiero.

Entonces con eso en mente

- Paso A : preparando la biblioteca
    - Cortamos los documentos en pedazos y cada trozo es convertido a un vector usando un modelo de embeddings
    - Guardamos esos vectores en una Vector Database


- Paso B : Recuperacion (Retrieval)
    - La pregunta del usuario es convertido en un vector , buscando mediante similtud coseno en la base de datos, 3 o 5 textos mas parecidos constituiran en **c_t**

- Paso C :El aumento (Augmentation)
    - Antes de llamar a Ollama se inyecta esos textos en la consulta(prompt de usuario) ej : **"Basándote en este contexto: [Texto Recuperado $c_t$], responde a la pregunta: [Pregunta del usuario $h_t$]".**

De tal modo que el agente no tendra que leer un dccumento de 500 paginas, el servidor rag busca en las 500 paginas y entrega al llm solo las 2 frases que se necesita (esto es algo un poco abstracto)

RAG es la capacidad de memoria externa , buscamos conocimiento que no cabe en el prompt

**app/memory/server_rag.py**

```bash
import numpy as np
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Servidor-RAG")
VECTOR_DATABASE = []

def get_embedding(text):
    try:
        response = requests.post(
            "http://ollama-server:11434/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        return np.array(response.json()["embedding"])
    except:
        return None

@mcp.tool()
def memorizar_informacion(texto: str) -> str:
    """Guarda información en la memoria vectorial."""
    vector = get_embedding(texto)
    if vector is not None:
        VECTOR_DATABASE.append({"texto": texto, "vector": vector})
        return f"Dato guardado."
    return "Error al indexar."

@mcp.tool()
def recuperar_contexto(pregunta: str) -> str:
    """Recupera los 2 fragmentos más similares a la pregunta."""
    if not VECTOR_DATABASE: return "Memoria vacía."
    v_query = get_embedding(pregunta)
    if v_query is None: return "Error en embedding."

    scores = []
    for item in VECTOR_DATABASE:
        v_doc = item["vector"]
        # Similitud Coseno
        sim = np.dot(v_query, v_doc) / (np.linalg.norm(v_query) * np.linalg.norm(v_doc))
        scores.append((item["texto"], sim))

    scores.sort(key=lambda x: x[1], reverse=True)
    return "\n".join([s[0] for s in scores[:2]])
```

**app/mcp.py**

```bash
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVIDORES_CONFIG = {
    # Servidor de Herramientas (usando la ruta de tu carpeta tools)
    "tools": StdioServerParameters(
        command="python",
        args=["-m", "app.tools.server_mcp"] 
    ),
    # Servidor de Memoria (usando la ruta de tu carpeta memory)
    "memory": StdioServerParameters(
        command="python",
        args=["-m", "app.memory.server_rag"]
    ),
    # Servidor externo de la comunidad (opcional, requiere node)
    "files": StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/mnt/g/Esau/2025_3/agentes"]
    )
}

class MCPManager:
    def __init__(self):
        self.sessions = []
        self.exit_stack = AsyncExitStack()

    async def conectar_todos(self):
        tools_totales = []
        for nombre, params in SERVIDORES_CONFIG.items():
            try:
                read, write = await self.exit_stack.enter_async_context(stdio_client(params))
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                lista = await session.list_tools()
                tools_totales.extend(lista.tools)
                self.sessions.append(session)
                print(f" Conectado a: {nombre}")
            except Exception as e:
                print(f" Falló conexión a {nombre}: {e}")
        return tools_totales

    async def ejecutar_en_cualquiera(self, nombre_tool, argumentos):
        for session in self.sessions:
            try:
                resultado = await session.call_tool(nombre_tool, arguments=argumentos)
                return resultado.content[0].text
            except:
                continue
        raise ValueError(f"Herramienta '{nombre_tool}' no encontrada.")

    async def cerrar(self):
        await self.exit_stack.aclose()
```

**app/agente.py**

```bash
import json
from .llm import llamada_a_modelo
from .mcp import MCPManager

async def iniciar_agente(input_usuario):
    manager = MCPManager()
    try:
        # 1. Handshake y Descubrimiento
        tools_disponibles = await manager.conectar_todos()
        desc_tools = "\n".join([f"- {t.name}: {t.description}" for t in tools_disponibles])

        # 2. PASO RAG (Retrieval): ct = Recuperar context de server_rag
        contexto_extra = ""
        try:
            # Llamamos a la herramienta del server_rag
            contexto_extra = await manager.ejecutar_en_cualquiera(
                "recuperar_contexto", 
                {"pregunta": input_usuario}
            )
        except:
            contexto_extra = "No se encontró contexto relevante."

        # 3. Augmentation: Inyectamos ct en el prompt del sistema
        prompt_sistema = f"""
        Solo responde en JSON.
        
        CONTEXTO DE MEMORIA (RAG):
        {contexto_extra}
        
        HERRAMIENTAS DISPONIBLES:
        {desc_tools}

        Si necesitas una herramienta: {{"herramienta_llamada": "nombre", "parametros": {{...}}}}
        Si tienes la respuesta final: {{"respuesta": "texto"}}
        """

        h_t = [{"role": "user", "content": input_usuario}]
        
        while True:
            # 4. Generation: a_t ~ Pθ(a_t | h_t, c_t)
            a_t = llamada_a_modelo(h_t, prompt_sistema)
            a_t = a_t.strip().replace("```json", "").replace("```", "")

            try:
                a_t_ = json.loads(a_t)
                
                if "herramienta_llamada" in a_t_:
                    # Ejecución dinámica en cualquier servidor conectado
                    o_t = await manager.ejecutar_en_cualquiera(
                        a_t_["herramienta_llamada"], 
                        a_t_["parametros"]
                    )
                    print(f"Output herramienta: {o_t}")
                    
                    h_t.append({"role": "assistant", "content": a_t})
                    h_t.append({"role": "user", "content": f"Resultado: {o_t}"})
                    continue
                
                return a_t_.get("respuesta", a_t)

            except json.JSONDecodeError:
                return a_t
    finally:
        await manager.cerrar()
```

**Dockerfile**

```bash
FROM python:3.11-slim

# Instalamos Node.js para los servidores MCP de la comunidad
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalamos dependencias primero (mejor para la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto al WORKDIR (/app)
COPY . .

# El PYTHONPATH debe apuntar a la raíz del proyecto DENTRO del contenedor
# Esto permite que 'import app.mcp' funcione desde cualquier subcarpeta
ENV PYTHONPATH=/app

CMD ["python", "-m", "app.main"]
```
**ODOO** 



Finalmente odoo es un ERP modular (Enterprise Resource Planning) Incluye:
- CRM (customer relationship management) gestion de relaciones con el cliente.Es una estrategia como categorica de software,analiza las interacciones de una empresa con sus cliente.
- Gestiona eficientemente las relaciones comerciales
- Agiliza tareas como seguimiento de leads y correos
- Utiliza datos para segmentar y predecir comportamiento

Es un backend empresarial con API

Se integra en la arquitectura como un servidor mcp mas

**server_odoo.py**

```bash
    from mcp.server.fastmcp import FastMCP
import xmlrpc.client

mcp = FastMCP("Servidor-Odoo")

url = "http://odoo:8069"
db = "mi_db"
username = "admin"
password = "admin"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

@mcp.tool()
def obtener_cliente(nombre: str) -> str:
    clientes = models.execute_kw(
        db, uid, password,
        'res.partner', 'search_read',
        [[['name', 'ilike', nombre]]],
        {'fields': ['name', 'email']}
    )
    return str(clientes)

if __name__ == "__main__":
    mcp.run()
```
**mcp.py**

```bash
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVIDORES_CONFIG = {

    # Servidor de herramientas locales
    "tools": StdioServerParameters(
        command="python",
        args=["-m", "app.tools.server_mcp"]
    ),

    # Servidor RAG
    "memory": StdioServerParameters(
        command="python",
        args=["-m", "app.memory.server_rag"]
    ),

    # Servidor Odoo
    "odoo": StdioServerParameters(
        command="python",
        args=["-m", "app.erp.server_odoo"]
    ),

    # Servidor filesystem oficial MCP
    "files": StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/mnt/data"]
    ),

    # Servidor PostgreSQL MCP
    "postgres": StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-postgres",
            "postgresql://usuario:password@localhost:5432/mi_base"
        ]
    ),

    # Google Maps MCP
    "maps": StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-google-maps"],
        env={"GOOGLE_MAPS_API_KEY": "TU_API_KEY"}
    )
}

class MCPManager:
    def __init__(self):
        self.sessions = []
        self.exit_stack = AsyncExitStack()

    async def conectar_todos(self):
        tools_totales = []
        for nombre, params in SERVIDORES_CONFIG.items():
            try:
                read, write = await self.exit_stack.enter_async_context(stdio_client(params))
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                lista = await session.list_tools()
                tools_totales.extend(lista.tools)
                self.sessions.append(session)
                print(f" Conectado a: {nombre}")
            except Exception as e:
                print(f" Falló conexión a {nombre}: {e}")
        return tools_totales

    async def ejecutar_en_cualquiera(self, nombre_tool, argumentos):
        for session in self.sessions:
            try:
                resultado = await session.call_tool(nombre_tool, arguments=argumentos)
                return resultado.content[0].text
            except:
                continue
        raise ValueError(f"Herramienta '{nombre_tool}' no encontrada.")

    async def cerrar(self):
        await self.exit_stack.aclose()
```
