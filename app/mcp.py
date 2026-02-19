from .tools import consultar_empresa,buscar_documentos,ejecutar_codigo


TOOLS = {
    "consultar_empresa":consultar_empresa,
    "buscar_documentos":buscar_documentos,
    "ejecutar_codigo":ejecutar_codigo
}

def ejecutar_herramienta(nombre, parametros):
    if nombre not in TOOLS:
        raise ValueError(f"{nombre} no existe")
    return TOOLS[nombre](**parametros)
