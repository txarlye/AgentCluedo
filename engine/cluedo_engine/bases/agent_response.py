from pydantic   import BaseModel, Field
from typing     import Optional

class AgentResponse(BaseModel):
    """
    Definimos la estructura de CUALQUIER respuesta de un agente
    """
    # Usamos Field(...) para dar descripciones al LLM
    dialogo: str = Field(description="El diálogo hablado por el personaje")
    
    accion: Optional[str] = Field(
        description="Una breve descripción de la acción o emoción del personaje (ej. 'sonríe sarcásticamente', 'mira por la ventana'). Si no hay acción, dejar como 'None'.",
        default=None
    )
    