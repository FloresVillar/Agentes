import json
from .llm import llamada_a_modelo
from .mcp import ejecutar_herramienta

PROMPT = """
Tu eres un un agente ia que usa el modelo claude, puedes hacer:

1. Responder directamente al usuario 
2. Llamar(usar) herramientas usando formato JSON (de momento):
{
    "herramienta_llamada":"nombre_herramienta",
    "parametros":{ ... }
}

Cuando sea necesario usa herramienta_consultada.
Cuando tengas la informacion suficiente(la buscada) ,responde normalmente.
"""

def iniciar_agente(input):
    h_t = [{"role":"user","content":input}]
    while True:
        a_t = llamada_a_modelo(h_t,PROMPT)                                #a_t ~ Pθ(a_T | h_t )
        try:
            a_t_ = json.loads(a_t)
            if "herramienta_llamada" in a_t_:
                nombre_herramienta = a_t_["herramienta_llamada"]
                parametros = a_t_["parametros"]
                o_t = ejecutar_herramienta(nombre_herramienta,parametros)   #o_t = E(T_i,params)
                print(f"output del entorno: {o_t}\n")
                h_t.append({"role":"asisstant","content":a_t})
                h_t.append({"role":"tool","content":str(o_t)})  #h_t+1 = h_T  + a_t  +  o_t
                continue # si a_t  es final sale del try y retorna
        except json.JSONDecodeError:
            pass
        print(f"Respuesta final:{a_t}")
        return a_t