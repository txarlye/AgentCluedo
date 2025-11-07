from langchain_core.tools import StructuredTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.messages import HumanMessage,AIMessage
from pydantic import BaseModel, Field

from .llm_factory           import get_llm
from .bases.base_agent      import AgenteBase
from .utils.prompt_loader   import load_prompt

from .detective_agent import crear_agente_detective

class InterrogarArgs(BaseModel):
    sospechoso: str = Field(description="Nombre del sospechoso (ej: 'Mayordomo', 'Heredera')")
    pregunta: str = Field(description="La pregunta exacta que quieres hacer")

class BuscarPistaArgs(BaseModel):
    ubicacion: str = Field(description="La ubicación a buscar (ej: 'biblioteca', 'cocina')")

class AcusarArgs(BaseModel):
    sospechoso: str = Field(description="Nombre del sospechoso que acusas")
    
    
class GameManager:
    """
    El Orquestador principal del juego
    Contiene los estados del juego, sospechosos y el detective
    """
    
    def __init__(self):
        print("Creando GameManager . . . \n")
        
        # 1. El cerebro (LLM)
        self.llm = get_llm()
        
        # 2. El historial del chat
        self.chat_history = []
        
        # 3. Creamos los sospechosos
        self.mayordomo  = AgenteBase(
            nombre      = "Alfred (Mayordomo)",
            rol_prompt  = load_prompt("mayordomo.md"),
            llm         = self.llm        
        )
        self.heredera   = AgenteBase(
            nombre      = "Beatrice (Heredera)",
            rol_prompt  = load_prompt("heredera.md"),
            llm         = self.llm        
        )
        
        # 4. Diccionario para encontrar agentes por nombre
        self.sospechosos = {
            "mayordomo": self.mayordomo,
            "heredera" : self.heredera,
        }
        
        herramientas_reales = [
            # ¡Cambiamos 'Tool' por 'StructuredTool'!
            StructuredTool(
                name="interrogar",
                func=self.interrogar, 
                description="Usa esta herramienta para interrogar a un sospechoso. Especifica el nombre (ej: 'Mayordomo', 'Heredera') y la pregunta.",
                args_schema=InterrogarArgs
            ),
            # ¡Cambiamos 'Tool' por 'StructuredTool'!
            StructuredTool(
                name="buscar_pista",
                func=self.buscar_pista,
                description="Usa esta herramienta para buscar pistas en una ubicación específica de la mansión (ej: 'biblioteca', 'cocina', 'habitación de la víctima').",
                args_schema=BuscarPistaArgs
            ),
            # ¡Cambiamos 'Tool' por 'StructuredTool'!
            StructuredTool(
                name="acusar",
                func=self.acusar,
                description="Usa esta herramienta SÓLO cuando estés 100% seguro de quién es el asesino. Esto termina el juego.",
                args_schema=AcusarArgs
            )
        ]
        
        # 5. Creamos el Agente
        self.detective = crear_agente_detective(
            llm=self.llm, 
            tools_list=herramientas_reales
        )
        
        
        
        
        print("GameManager Listo")
        
    
    def interrogar(self, sospechoso: str, pregunta: str) -> str:
        print(f"DEBUG: [Herramienta 'interrogar' REAL] -> {sospechoso}")
        
        nombre_sospechoso = sospechoso.lower()
        if nombre_sospechoso not in self.sospechosos:
            return f"Error: No existe un sospechoso llamado '{sospechoso}'."
        
        agente_sospechoso = self.sospechosos[nombre_sospechoso]
        respuesta_agente = agente_sospechoso.invoke(pregunta, history=self.chat_history)
        
        return f"Respuesta de {sospechoso}: {respuesta_agente.dialogo}"

    def buscar_pista(self, ubicacion: str) -> str:
        print(f"DEBUG: [Herramienta 'buscar_pista' REAL] -> {ubicacion}")
        
        if ubicacion.lower() == "biblioteca":
            return "Buscas en la biblioteca y encuentras un diario con una página arrancada."
        elif ubicacion.lower() == "cocina":
            return "Buscas en la cocina y encuentras un cuchillo sospechosamente limpio."
        elif ubicacion.lower() == "habitación de la víctima":
            return "Buscas en la habitación de Lord Alistair y encuentras una carta de amenaza sin firmar."
        else:
            return f"Buscas en {ubicacion} pero no encuentras nada de interés."

    def acusar(self, sospechoso: str) -> str:
        print(f"DEBUG: [Herramienta 'acusar' REAL] -> {sospechoso}")
        
        if sospechoso.lower() == "heredera": # (La 'verdad' secreta)
            return "¡Correcto! Has acusado a la Heredera. ¡HAS GANADO! Ella confiesa."
        else:
            return f"Has acusado a {sospechoso}. Es inocente. ¡HAS PERDIDO!"

    # --- MÉTODO PARA CORRER EL JUEGO ---
    def run_game(self):
        print("\n--- ¡Comienza el Juego! ---")
        objetivo = """
        Ha habido un asesinato en la mansión. 
        La víctima es Lord Alistair. 
        Los sospechosos son 'Mayordomo' y 'Heredera'.
        La 'verdad' secreta del juego es que la 'Heredera' es la culpable.
        Tu objetivo es descubrir la verdad usando tus herramientas. Empieza a investigar.
        ¡Piensa y habla en español!
        """
        
        # El prompt del Hub (hwchase17/openai-tools-agent) espera 'input'
        resultado = self.detective.invoke({
            "input": objetivo,
            "chat_history": self.chat_history
        })
        
        print("\n--- Respuesta Final del Detective ---")
        print(resultado["output"])
        print("--- Juego Terminado ---")