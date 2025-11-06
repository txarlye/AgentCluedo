from agents.llm_factory import get_llm
from settings.settings import settings

class Bot():
    def __init__(self,boot_provider):
        self.llm = get_llm()
        print(f"iniciando boot {boot_provider}") 
    def start_chat(self):
        print("---")
        print("-Chat iniciado. Escribe 'exit' para salir")
        
        while True:
            try:
                user_input = input("Tú: ")
                if user_input.lower() == 'exit':
                    print("salimos")
                    break
                print("Bot pensando...") 
                 
                respuesta = self.llm.invoke(user_input)
                print(f"Bot: {respuesta.content}")
                
            except EOFError:
                print("\n adios !")
                break
            except KeyboardInterrupt:
                print("\n adios !")
                break