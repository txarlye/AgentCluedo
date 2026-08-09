import boto3

from config import settings


def get_dynamo_resource():
    kwargs = {"region_name": settings.aws_region}
    if settings.dynamodb_endpoint_url:
        # DynamoDB Local no valida credenciales, pero boto3 exige que existan.
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
        kwargs["aws_access_key_id"] = "local"
        kwargs["aws_secret_access_key"] = "local"
    return boto3.resource("dynamodb", **kwargs)
