
def consultar_empresa(nombre):
    mock = {
        "Empresa X":100,
        "Empresa Y":200
    }
    return {"empleados":mock.get(nombre,"No hallado")}

def buscar_documentos(nombre_documento):
    return {"documento","DOCUMENTO_ENCONTRADO"}

def ejecutar_codigo(nombre_funcion):
    return {"codigo":"CODIGO_EJECUTADO"}