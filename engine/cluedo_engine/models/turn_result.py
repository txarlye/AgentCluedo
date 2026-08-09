from typing import Literal, Optional

from pydantic import BaseModel, Field


class AgentTurnResult(BaseModel):
    """Resultado de un turno del detective, sin ningún print/input de por medio."""

    final_response: str
    observations: list[str] = Field(default_factory=list)
    is_game_over: bool = False
    result: Optional[Literal["won", "lost"]] = None
