from settings.settings import settings
from UI.console.console_base import ConsoleBase
from agents.llm_factory import get_llm
from UI.console.chat_bot import Bot




def main():
    print("Hello from agentcluedo!")
    
    # consola:
    # console = ConsoleBase(settings.main_name)
    # console.show_menu()
    
    #Test chatbot
    # my_bot = Bot(settings.agentes)
    # my_bot.start_chat()
    
    
    

if __name__ == "__main__":
    main()
