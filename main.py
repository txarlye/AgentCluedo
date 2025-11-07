from settings.settings import settings
from UI.console.console_base import ConsoleBase
from agents.llm_factory import get_llm
from UI.console.chat_bot import Bot
from agents.utils.prompt_loader import load_prompt
from agents.bases.base_agent import AgenteBase
from minigames.game_2_agentes_hablando import dos_agentes_hablando
from minigames.game_3_detective_autonomo import probar_detective
from agents.game_manager import GameManager

def test_chatbot():
    #Test chatbot
    my_bot = Bot(settings.agentes)
    my_bot.start_chat()
def test_consola():
    # consola:
    console = ConsoleBase(settings.main_name)
    console.show_menu()
   
def main():
    print("Hello from agentcluedo!")
    # dos_agentes_hablando()
    # probar_detective()
    juego = GameManager()
    juego.run_game()
     
if __name__ == "__main__":
    main()
