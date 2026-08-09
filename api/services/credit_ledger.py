from datetime import datetime, timezone

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from config import settings
from services.dynamo import get_dynamo_resource

_dynamo = get_dynamo_resource()
_users_table = _dynamo.Table(settings.users_table)


class InsufficientCreditsError(Exception):
    pass


def get_or_create_user(user_id: str, email: str) -> dict:
    resp = _users_table.get_item(Key={"user_id": user_id})
    item = resp.get("Item")
    if item:
        return item

    item = {
        "user_id": user_id,
        "email": email,
        "credits_balance": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _users_table.put_item(Item=item)
    return item


def get_credits(user_id: str) -> int:
    resp = _users_table.get_item(Key={"user_id": user_id})
    item = resp.get("Item")
    return int(item["credits_balance"]) if item else 0


def grant_credits(user_id: str, amount: int) -> int:
    resp = _users_table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="ADD credits_balance :n",
        ExpressionAttributeValues={":n": amount},
        ReturnValues="UPDATED_NEW",
    )
    return int(resp["Attributes"]["credits_balance"])


def consume_credit(user_id: str) -> int:
    """Descuenta 1 crédito de forma atómica. Lanza InsufficientCreditsError si no hay saldo."""
    try:
        resp = _users_table.update_item(
            Key={"user_id": user_id},
            UpdateExpression="ADD credits_balance :minus_one",
            ConditionExpression=Attr("credits_balance").gt(0),
            ExpressionAttributeValues={":minus_one": -1},
            ReturnValues="UPDATED_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise InsufficientCreditsError(f"El usuario {user_id} no tiene créditos.") from e
        raise
    return int(resp["Attributes"]["credits_balance"])
