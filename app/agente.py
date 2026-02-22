import json
from .llm import llamada_a_modelo
from .mcp import ejecutar_herramienta

PROMPT = """ 
Solo JSON.

Herramienta:
{"herramienta_llamada":"consultar_empresa","parametros":{"nombre":"Empresa X"}}

Respuesta:
{"respuesta":"texto"}

"""

def iniciar_agente(input):
    h_t = [{"role":"user","content":input}]
    ya_ejecuto = False
    while True:
        a_t = llamada_a_modelo(h_t,PROMPT)              #a_t ~ Pθ(a_T | h_t )
        a_t = a_t.strip()
        if a_t.startswith("```"):
            a_t = a_t.replace("```json", "").replace("```", "").strip()
        try:
            a_t_ = json.loads(a_t)
            if "herramienta_llamada" in a_t_ and not ya_ejecuto:
                ya_ejecuto = True
                nombre_herramienta = a_t_["herramienta_llamada"]
                parametros = a_t_["parametros"]
                o_t = ejecutar_herramienta(nombre_herramienta,parametros)   #o_t = E(T_i,params)
                print(f"output del entorno: {o_t}\n")
                h_t.append({"role":"assistant","content":a_t})
                h_t.append({"role":"user","content":f"resultado de herramienta: {o_t}"})  #h_t+1 = h_T  + a_t  +  o_t
                continue # si a_t  es final sale del try y retorna
        except json.JSONDecodeError:
            pass
        print(f"Respuesta final:{a_t}")
        return a_t