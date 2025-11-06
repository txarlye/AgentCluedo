from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI 
from settings.settings import settings

def get_llm():
    provider = settings.agentes
    
    if provider == "ollama":
        return ChatOllama(model=settings.ollama_model)
    
    if provider == "openai":
        return ChatOpenAI(api_key=settings.OPEN_AI_API)
    
    else:
        raise ValueError(f"Proveedor no soportado {provider}")