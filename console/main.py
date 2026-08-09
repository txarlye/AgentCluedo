from settings.settings import settings
from cluedo_engine.llm_factory import get_llm
from cluedo_engine.game_manager import GameManager
from game_loop import run_game


def main():
    print("Hello from agentcluedo!")

    llm = get_llm(
        provider=settings.agentes,
        ollama_model=settings.ollama_model,
        openai_api_key=getattr(settings, "OPEN_AI_API", None),
    )
    juego = GameManager(llm)
    run_game(juego)


if __name__ == "__main__":
    main()
