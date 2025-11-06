from settings.settings import settings
from UI.console.console_base import ConsoleBase
from agents.llm_factory import get_llm
from UI.console.chat_bot import Bot
from agents.utils.prompt_loader import load_prompt
from agents.bases.base_agent import AgenteBase
from langchain_core.messages import AIMessage,HumanMessage


def dos_agentes_hablando():
    """agentes hablando entre ellos
    """
    llm = get_llm()
    # Cargamos las personalidades
    prompt_mayordomo    = load_prompt("mayordomo.md")
    prompt_heredera     = load_prompt("heredera.md")
    
    # creamos las instancias de los agentes
    mayordomo = AgenteBase(
        nombre = "Alfred (Mayordomo)",
        rol_prompt= prompt_mayordomo,
        llm=llm
    )
    heredera = AgenteBase(
        nombre="Beatrice (Heredera)",
        rol_prompt= prompt_heredera,
        llm=llm
    )
    
    conversation_history: list[HumanMessage | AIMessage] = []
    
    # 4. ¡LA ORQUESTACIÓN!
    # El 'Game Master' (nosotros) inicia la conversación.
    pregunta_actual = "Señorita Beatrice, la he visto discutir con la víctima esta mañana. ¿Qué tiene que decir?"
     
    for turno in range(3):
        print(f"--- TURNO  {turno+1} ---")
        
        print(f" Game Master (a Heredera): {pregunta_actual}\n")
        
        # llamamos a la heredera pasándole el historial
        msg_heredera = heredera.invoke(pregunta_actual, history=conversation_history)
        print(f"[-Accion- Beatrice (Heredera)]: *{msg_heredera.accion}*")
        print(f"[-Dialogo- Beatrice (Heredera)]: {msg_heredera.dialogo}*")
        
        # Actualizamos memoria
        conversation_history.append(HumanMessage(content=pregunta_actual))
        conversation_history.append(AIMessage(content=msg_heredera.dialogo))
        
        # Turno del Mayordomo
        pregunta_a_mayordomo = f"Mayordomo, ¿qué opina de lo que acaba de decir la señorita Beatrice? (Ella dijo: '{msg_heredera.dialogo}')"
        print(f"Game Master (a Mayordomo): {pregunta_a_mayordomo}\n")
        # Lo llamamos, PASANDO el historial (que ahora incluye la respuesta de Beatrice)
        msg_mayordomo = mayordomo.invoke(pregunta_a_mayordomo, history=conversation_history)
        print(f"Acción [Alfred]: *{msg_mayordomo.accion}*")
        print(f"Diálogo [Alfred]: {msg_mayordomo.dialogo}\n")
        # ACTUALIZAMOS LA MEMORIA OTRA VEZ
        conversation_history.append(HumanMessage(content=pregunta_a_mayordomo))
        conversation_history.append(AIMessage(content=msg_mayordomo.dialogo))
        # Preparamos la siguiente pregunta (para que la Heredera reaccione al Mayordomo)
        pregunta_actual = f"Señorita Beatrice, el Mayordomo dice: '{msg_mayordomo.dialogo}'. ¿Qué responde a eso?"
    
    print("---" * 10)
    print("Simulación con memoria terminada.")