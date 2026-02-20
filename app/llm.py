from openai import OpenAI
# from anthropic import Anthropic  
import os
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

#cliente = OpenAI(api_key="ollama",base_url="http://localhost:11434/v1")
# cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))  # VERSIÓN ANTERIOR
cliente = OpenAI(api_key="ollama",base_url=os.getenv("OLLAMA_HOST")+"/v1")

def llamada_a_modelo(historial, prompt): 
    mensajes = [{"role": "system", "content": prompt}] + historial
    accion = cliente.chat.completions.create(model="llama2",messages=mensajes,max_tokens=500)
    return accion.choices[0].message.content

# VERSIÓN ANTERIOR CON ANTHROPIC:
# def llamada_a_modelo(historial,prompt):
#     accion = cliente.messages.create(
#         model="claude-3-5-sonnet-latest",
#         max_tokens=500,
#         messages=historial,
#         system=prompt
#     )
#     return accion.content[0].text