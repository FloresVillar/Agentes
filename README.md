# USO DE AGENTES

Segun gpt un agente es un SISTEMA que 
- Percibe informacion (recibe?)
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

**RAG**

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
- Reduce alucinaciones (ahora el agentes es un llm que accede a la data)
- No necesita fine-tunning

Aunque se complementan