# agents/detective_agent.py

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models.chat_models import BaseChatModel
from typing import List
from langchain import hub # Para descargar el prompt estándar

def crear_agente_detective(llm: BaseChatModel, tools_list: List) -> AgentExecutor:
    """
    Esta 'fábrica' construye y devuelve el Agente Detective ejecutable.
    Recibe el LLM y la lista de herramientas reales.
    """ 
    print("Fábrica: Creando agente detective...")
    
    # 1. Obtenemos el prompt estándar para "Tool Calling" desde el Hub.
    #    Este prompt (hwchase17/openai-tools-agent) está optimizado
    #    para que el LLM llame a herramientas de forma fiable.
    prompt = hub.pull("hwchase17/openai-tools-agent")

    # 2. Creamos el agente (el cerebro)
    agent = create_tool_calling_agent(
        llm     = llm,
        tools   = tools_list,
        prompt  = prompt
    )
    
    # 3. Creamos el ejecutor del agente (el motor)
    agent_executor = AgentExecutor(
        agent   = agent,
        tools   = tools_list,
        verbose = True 
    )
    
    return agent_executor




# PROMPT_ESPANOL = """
# Eres un detective de renombre mundial, famoso por tu lógica y astucia.
# Tu objetivo es resolver el asesinato de Lord Alistair.
# Habla y piensa SIEMPRE en español.

# Tienes acceso a las siguientes herramientas:
# {tools}

# Aquí está cómo funciona el bucle de pensamiento:
# 1.  **Pensamiento:** Piensa paso a paso cuál es tu plan.
# 2.  **Acción:** Decide si necesitas usar una herramienta para obtener más información.
# 3.  **Observación:** Recibirás el resultado de la herramienta.
# 4.  Repite hasta que tengas una respuesta final.

# **REGLAS DE FORMATO MUY IMPORTANTES:**
# * **Si decides usar una herramienta:** Tu respuesta debe ser *solo* el bloque JSON de la herramienta. No añadas texto de "pensamiento" antes o después.
# * **Si decides que tienes suficiente información:** Tu respuesta debe ser *solo* el texto de tu respuesta final (sin JSON).

# Historial de la conversación (para tener contexto):
# {chat_history}

# Instrucción/Pregunta del usuario:
# {user_input}

# A continuación, proporciona tu pensamiento y la acción a tomar (si es necesaria).
# O, si ya tienes la respuesta, proporciona la respuesta final.
# {agent_scratchpad}
# """