# from langchain_community.chat_models import ChatOllama
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI 
from settings.settings import settings

def get_llm():
    provider = settings.agentes
    
    if provider == "ollama":
        print(f"✅ Usando Ollama (Modelo: {settings.ollama_model})")
        # Creamos la instancia
        llm = ChatOllama(model = settings.ollama_model)
        
        # forzamos a usar json
        
        return llm.bind(format = "json")
    
    if provider == "openai":
        print("✅ Usando OpenAI")
        return ChatOpenAI(api_key=settings.OPEN_AI_API)
    
    else:
        raise ValueError(f"Proveedor no soportado {provider}")