from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from .agent_response import AgentResponse
from langchain_core.prompts import ChatPromptTemplate  
import json

class AgenteBase:
    """
    La clase base para todos nuestros agentes del juego (Sospechosos).
    """
    def __init__(self, nombre: str, rol_prompt: str, llm: BaseChatModel):
        self.nombre = nombre
        
        # 1. Creamos un prompt template (más robusto)
        #    (Ya no necesitamos las 'format_instructions' manuales)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", rol_prompt + "\n\nResponde SIEMPRE usando la estructura JSON solicitada."),
            ("placeholder", "{history}"),
            ("human", "{input}")
        ])
        self.chain = self.prompt | llm.with_structured_output(AgentResponse)
    
    def invoke(self, entrada: str, history: list[HumanMessage | AIMessage]) -> AgentResponse:
        """
        Llama al agente para que genere una respuesta estructurada.
        """
        print(f"DEBUG: Agente '{self.nombre}' está pensando (con {len(history)} mensajes en memoria)...")
        
        try:
            # 3. Invocamos la CADENA, no el LLM directamente
            respuesta = self.chain.invoke({
                "history": history,
                "input": entrada
            })
            # 'respuesta' ya es un objeto AgentResponse validado
            return respuesta
        
        except Exception as e:
            # Capturamos cualquier error de validación
            print(f"ERROR: No se pudo parsear la respuesta de {self.nombre}. Error: {e}")
            return AgentResponse(
                dialogo="Error: No pude procesar mi respuesta. (Fallo de parseo)", 
                accion="mira confundido"
            )
        