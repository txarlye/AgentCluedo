"""Crea (si no existen) las tablas DynamoDB en DynamoDB Local. Idempotente."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from botocore.exceptions import ClientError

from config import settings
from services.dynamo import get_dynamo_resource


def ensure_table(dynamo, name: str, key_name: str) -> None:
    try:
        dynamo.meta.client.describe_table(TableName=name)
        print(f"[ok] {name} ya existe")
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    dynamo.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": key_name, "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": key_name, "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamo.meta.client.get_waiter("table_exists").wait(TableName=name)
    print(f"[creada] {name}")


def main():
    dynamo = get_dynamo_resource()
    ensure_table(dynamo, settings.games_table, "game_id")
    ensure_table(dynamo, settings.users_table, "user_id")
    ensure_table(dynamo, settings.stripe_events_table, "event_id")


if __name__ == "__main__":
    main()
