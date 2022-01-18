from os import getenv

from boto3 import client


def get_queue_details(queue_name: str) -> None:
    sqs = client("sqs")
    response = sqs.get_queue_attributes(
        QueueUrl=f'https://sqs.{getenv("AWS_REGION")}.amazonaws.com/{getenv("AWS_ACCOUNT_ID")}/{queue_name}',
        AttributeNames=["All"],
    )
    return response
