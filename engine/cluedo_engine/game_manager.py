from langchain_core.tools import StructuredTool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field

from .bases.base_agent import AgenteBase
from .utils.prompt_loader import load_prompt
from .detective_agent import crear_agente_detective
from .models.turn_result import AgentTurnResult


class InterrogarArgs(BaseModel):
    sospechoso: str = Field(description="Nombre del sospechoso (ej: 'Mayordomo', 'Heredera')")
    pregunta: str = Field(description="La pregunta exacta que quieres hacer")

class BuscarPistaArgs(BaseModel):
    ubicacion: str = Field(description="La ubicación a buscar (ej: 'biblioteca', 'cocina')")

class AcusarArgs(BaseModel):
    sospechoso: str = Field(description="Nombre del sospechoso que acusas")


class GameManager:
    """
    El Orquestador principal del juego.
    Contiene los estados del juego, sospechosos y el detective.
    No hace ningún print()/input() — eso es responsabilidad de quien lo use
    (la consola hoy, una API mañana).
    """

    def __init__(self, llm: BaseChatModel):
        print("Creando GameManager . . . \n")

        # 1. El cerebro (LLM), ya construido por quien nos crea
        self.llm = llm

        # 2. El historial del chat
        self.chat_history = []

        # 3. Estado de fin de partida
        self.game_over = False
        self.game_result: str | None = None

        # 4. Creamos los sospechosos
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

        # 5. Diccionario para encontrar agentes por nombre
        self.sospechosos = {
            "mayordomo": self.mayordomo,
            "heredera" : self.heredera,
        }

        herramientas_reales = [
            StructuredTool(
                name="interrogar",
                func=self.interrogar,
                description="Usa esta herramienta para interrogar a un sospechoso. Especifica el nombre (ej: 'Mayordomo', 'Heredera') y la pregunta.",
                args_schema=InterrogarArgs
            ),
            StructuredTool(
                name="buscar_pista",
                func=self.buscar_pista,
                description="Usa esta herramienta para buscar pistas en una ubicación específica de la mansión (ej: 'biblioteca', 'cocina', 'habitación de la víctima').",
                args_schema=BuscarPistaArgs
            ),
            StructuredTool(
                name="acusar",
                func=self.acusar,
                description="Usa esta herramienta SÓLO cuando estés 100% seguro de quién es el asesino. Esto termina el juego.",
                args_schema=AcusarArgs
            )
        ]

        # 6. Creamos el Agente
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

        self.game_over = True

        if sospechoso.lower() == "heredera": # (La 'verdad' secreta)
            self.game_result = "won"
            return "¡Correcto! Has acusado a la Heredera. ¡HAS GANADO! Ella confiesa."
        else:
            self.game_result = "lost"
            return f"Has acusado a {sospechoso}. Es inocente. ¡HAS PERDIDO!"

    def start_case(self) -> str:
        """Texto de briefing inicial del caso. Sin print(): lo pinta quien nos use."""
        return (
            "--- ¡Comienza el Juego! ---\n"
            "Ha habido un asesinato en la mansión.\n"
            "La víctima es Lord Alistair.\n"
            "Los sospechosos son 'Mayordomo' y 'Heredera'."
        )

    def step(self, human_input: str) -> AgentTurnResult:
        """Ejecuta un turno del detective y devuelve el resultado estructurado."""
        resultado = self.detective.invoke({
            "input": human_input,
            "chat_history": self.chat_history
        })

        ai_response = resultado["output"]

        observations = []
        if resultado.get("intermediate_steps"):
            for _accion, observacion in resultado["intermediate_steps"]:
                observations.append(observacion)

        self.chat_history.append(HumanMessage(content=human_input))
        self.chat_history.append(AIMessage(content=ai_response))

        return AgentTurnResult(
            final_response=ai_response,
            observations=observations,
            is_game_over=self.game_over,
            result=self.game_result,
        )
