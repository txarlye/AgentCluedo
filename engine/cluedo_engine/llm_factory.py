from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def get_llm(
    provider: str,
    *,
    ollama_model: str | None = None,
    openai_api_key: str | None = None,
) -> BaseChatModel:
    if provider == "ollama":
        print(f"✅ Usando Ollama (Modelo: {ollama_model})")
        return ChatOllama(model=ollama_model)

    if provider == "openai":
        print("✅ Usando OpenAI")
        return ChatOpenAI(api_key=openai_api_key)

    raise ValueError(f"Proveedor no soportado: {provider}")
