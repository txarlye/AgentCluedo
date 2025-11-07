from agents.detective_agent import crear_agente_detective
from langchain_core.messages import HumanMessage, AIMessage

def probar_detective():
    """
    Esta función prueba el Agente Detective Autónomo
    """
    print("--- Iniciando prueba del detective autonomo ---")
    
    # Creamos el agente (el que piensa y actua):
    detective = crear_agente_detective()
    
    # Definimos el historial del chat
    chat_history = []
    
    # Damos el OBJETIVO inicial al detective
    objetivo = """
    Ha habido un asesinato en la mansión.
    La víctiva es Lord Alistair.
    Los sospechosos son 'Mayordomo' y 'Heredera'
    Tu objetivo es encontrar al asesino.
    Empieza a investigar.
    """
    
    print(f"Detective, su objetivo: {objetivo} \n")
    
    # Ejecutamos el agente
    resultado = detective.invoke({
        "user_input":objetivo,
        "chat_history": chat_history
    })
    
    print("\n -- Respuesta Final del Detective ---")
    print(resultado["output"])
    print("--- Prueba Terminada ---")