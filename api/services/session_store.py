from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage

from config import settings
from services.dynamo import get_dynamo_resource

_dynamo = get_dynamo_resource()
_games_table = _dynamo.Table(settings.games_table)


def serialize_chat_history(messages: list) -> list[dict]:
    serialized = []
    for m in messages:
        role = "human" if isinstance(m, HumanMessage) else "ai"
        serialized.append({"role": role, "content": m.content})
    return serialized


def deserialize_chat_history(data: list[dict]) -> list:
    messages = []
    for item in data:
        if item["role"] == "human":
            messages.append(HumanMessage(content=item["content"]))
        else:
            messages.append(AIMessage(content=item["content"]))
    return messages


def create_game(game_id: str, user_id: str, model_provider: str, briefing: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "game_id": game_id,
        "user_id": user_id,
        "status": "active",
        "result": None,
        "chat_history": [],
        "briefing": briefing,
        "model_provider": model_provider,
        "created_at": now,
        "updated_at": now,
    }
    _games_table.put_item(Item=item)
    return item


def get_game(game_id: str) -> dict | None:
    resp = _games_table.get_item(Key={"game_id": game_id})
    return resp.get("Item")


def save_turn(game_id: str, chat_history: list, status: str, result: str | None) -> None:
    _games_table.update_item(
        Key={"game_id": game_id},
        UpdateExpression="SET chat_history = :ch, #s = :status, #r = :result, updated_at = :u",
        ExpressionAttributeNames={"#s": "status", "#r": "result"},
        ExpressionAttributeValues={
            ":ch": serialize_chat_history(chat_history),
            ":status": status,
            ":result": result,
            ":u": datetime.now(timezone.utc).isoformat(),
        },
    )
