from anthropic import Anthropic

import os

cliente = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def llamada_a_modelo(historial,prompt):
    accion = cliente.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=500,
        messages=historial,
        system=prompt
    )
    return accion.content[0].text