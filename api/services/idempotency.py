from datetime import datetime, timezone

from botocore.exceptions import ClientError

from config import settings
from services.dynamo import get_dynamo_resource

_dynamo = get_dynamo_resource()
_events_table = _dynamo.Table(settings.stripe_events_table)


def mark_event_processed(event_id: str) -> bool:
    """Intenta registrar el evento. Devuelve True si es la primera vez que se ve
    (hay que procesarlo) o False si ya se había procesado (ignorarlo)."""
    try:
        _events_table.put_item(
            Item={"event_id": event_id, "processed_at": datetime.now(timezone.utc).isoformat()},
            ConditionExpression="attribute_not_exists(event_id)",
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise
