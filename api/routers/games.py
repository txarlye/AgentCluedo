import uuid

from cluedo_engine.game_manager import GameManager
from cluedo_engine.llm_factory import get_llm
from cluedo_engine.models.turn_result import AgentTurnResult
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from config import settings
from deps import get_current_user_id
from services import credit_ledger, session_store

router = APIRouter(prefix="/v1/games", tags=["games"])


def _build_game_manager() -> GameManager:
    llm = get_llm(
        provider=settings.llm_provider,
        ollama_model=settings.ollama_model,
        openai_api_key=settings.openai_api_key,
    )
    return GameManager(llm)


class NewGameResponse(BaseModel):
    game_id: str
    briefing: str
    credits_balance: int


class TurnBody(BaseModel):
    input: str


class GameStateResponse(BaseModel):
    game_id: str
    status: str
    result: str | None
    briefing: str


@router.post("", response_model=NewGameResponse)
def new_game(user_id: str = Depends(get_current_user_id)) -> NewGameResponse:
    try:
        credits_balance = credit_ledger.consume_credit(user_id)
    except credit_ledger.InsufficientCreditsError as e:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(e)) from e

    gm = _build_game_manager()
    briefing = gm.start_case()

    game_id = str(uuid.uuid4())
    session_store.create_game(game_id, user_id, settings.llm_provider, briefing)

    return NewGameResponse(game_id=game_id, briefing=briefing, credits_balance=credits_balance)


@router.post("/{game_id}/turns", response_model=AgentTurnResult)
def play_turn(game_id: str, body: TurnBody, user_id: str = Depends(get_current_user_id)) -> AgentTurnResult:
    game = session_store.get_game(game_id)
    if game is None or game["user_id"] != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Caso no encontrado")
    if game["status"] != "active":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"El caso ya ha terminado (status={game['status']})")

    gm = _build_game_manager()
    gm.chat_history = session_store.deserialize_chat_history(game["chat_history"])

    resultado = gm.step(body.input)

    new_status = "won" if resultado.result == "won" else "lost" if resultado.result == "lost" else "active"
    session_store.save_turn(game_id, gm.chat_history, new_status, resultado.result)

    return resultado


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game(game_id: str, user_id: str = Depends(get_current_user_id)) -> GameStateResponse:
    game = session_store.get_game(game_id)
    if game is None or game["user_id"] != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Caso no encontrado")

    return GameStateResponse(
        game_id=game["game_id"],
        status=game["status"],
        result=game.get("result"),
        briefing=game["briefing"],
    )
