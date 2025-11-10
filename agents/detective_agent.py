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
        verbose = False ,
        return_intermediate_steps=True
    )
    
    return agent_executor
