from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from pathlib import Path
from dotenv import load_dotenv
import os

def crear_agente_detective(llm: BaseChatModel, tools_list: List) -> AgentExecutor:
    """
    Esta 'fábrica' construye y devuelve el Agente Detective ejecutable.
    Recibe el LLM y la lista de herramientas reales.
    """ 
    print("Fábrica: Creando agente detective...")
    
    # Desactivar LangSmith tracing para evitar errores 403
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_API_KEY"] = ""
    
    # Asegurarnos de que las variables de entorno estén cargadas
    env_path = Path(__file__).parent.parent / "settings" / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    
    # Prompt estándar de "Tool Calling", equivalente local a
    # hub.pull("hwchase17/openai-tools-agent"). Se define aquí directamente
    # en vez de descargarlo del Hub: el tracing se desactiva justo arriba
    # (LANGCHAIN_API_KEY vacío), así que esa llamada de red siempre
    # devolvía 403 y solo retrasaba el arranque.
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant. Use the available tools to answer the user's question.
If you don't know the answer, use the tools to find it. Be concise and accurate in your responses."""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

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
