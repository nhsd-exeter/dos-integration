from json import load
from os import getenv, remove
from time import sleep

from boto3 import client, resource

from integration.steps.functions.context import Context

S3_CLIENT = client("s3", region_name="eu-west-2")


def get_s3_email_file(context: Context) -> Context:
    """Get the email file from S3 bucket.

    Args:
        context (Context): Test context

    Returns:
        context (Context): Test context
    """
    sleep(45)
    email_file_name = "email_file.json"
    shared_environment = getenv("SHARED_ENVIRONMENT")
    bucket_name = f"uec-dos-int-{shared_environment}-send-email-bucket"
    response = S3_CLIENT.list_objects(Bucket=bucket_name)
    object_key = response["Contents"][-1]["Key"]
    s3_resource = resource("s3")
    s3_resource.meta.client.download_file(bucket_name, object_key, email_file_name)
    with open(email_file_name) as email_file:
        context.other = load(email_file)
    remove("./email_file.json")
    return context
