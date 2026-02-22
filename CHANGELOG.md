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

