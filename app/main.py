from .agente import iniciar_agente

def main():
    while True:
        entrada = input("Usuario:" )
        if entrada.lower() in ["salir","exit","quit"]:
            print("Terminando")
            break
        respuesta = iniciar_agente(entrada)
        #print(f"respuesta de agente {respuesta}\n")

if __name__=='__main__':
    main()

