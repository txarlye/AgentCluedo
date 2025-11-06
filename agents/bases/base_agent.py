from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from .agent_response import AgentResponse

class AgenteBase:
    """
    Este agente no sabe nada de los inputs y los print
    solo sabe "pensar" (invoke)
    """
    def __init__(self, nombre:str, rol_prompt: str,llm: BaseChatModel):
        self.nombre = nombre
        self.llm = llm
        
        # 1. configurar el Parser
        self.parser = PydanticOutputParser(pydantic_object = AgentResponse)
        # 2. obtener las instrucciones de formato
        format_instructions = self.parser.get_format_instructions()
        prompt_con_formato = f"""{rol_prompt} 
        {format_instructions}"""
        
        self.system_message = SystemMessage(content = prompt_con_formato)
    
    def invoke(self, entrada: str, 
               history: list[HumanMessage | AIMessage]) -> AgentResponse:
        """
        Llama al agente para generar respuesta estructurada
        """
        print(f" DEBUG: Agente '{self.nombre}' está pensando con {len(history)} mensajes en memoria...")
         
        # Creamos los mensajes para la llamada
        # 1. su personalidad
        # 2. la entrada humana del otro agente
        # más adelante los mensajes de la memoria
        mensajes = [self.system_message] + history + [HumanMessage(content=entrada)]
        
        # llamamos al LLM
        respuesta_llm = self.llm.invoke(mensajes)
        
        try:
            # respuesta_llm.content es el string JSON (ej. '{"dialogo": "...", "accion": "..."}')
            respuesta_parseada = self.parser.parse(respuesta_llm.content)
            return respuesta_parseada
        except Exception as e:
            print(f"ERROR: No se pudo parsear la respuesta de {self.nombre}. Error: {e}")
            print(f"Respuesta cruda: {respuesta_llm.content}")
            # Devolvemos un objeto de emergencia
            return AgentResponse(
                dialogo="Error: No pude procesar mi respuesta.", 
                accion="mira confundido"
            )
        