from json import dumps
from os import getenv
from random import randint
from time import time_ns

from boto3 import client

from integration.steps.functions.context import Context

SQS_CLIENT = client("sqs", region_name="eu-west-2")


def get_sqs_queue_name(queue_type: str) -> str:
    """Returns the SQS queue name for the specified queue type.

    Args:
        queue_type (str): The type of SQS queue to return

    Returns:
        queue_name (str): The name of the SQS queue
    """
    response = ""
    blue_green_environment = getenv("BLUE_GREEN_ENVIRONMENT")
    shared_environment = getenv("SHARED_ENVIRONMENT")
    match queue_type.lower():
        case "changeevent":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{shared_environment}-change-event-dead-letter-queue.fifo",
            )
        case "updaterequest":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{blue_green_environment}-update-request-dead-letter-queue.fifo",
            )
        case "updaterequestfail":
            response = SQS_CLIENT.get_queue_url(
                QueueName=f"uec-dos-int-{blue_green_environment}-update-request-queue.fifo",
            )
        case _:
            msg = "Invalid SQS queue type specified"
            raise ValueError(msg)

    return response["QueueUrl"]


def post_ur_sqs() -> None:
    """Post to update request SQS queue."""
    queue_url = get_sqs_queue_name("updaterequest")
    sqs_body = generate_sqs_body("https://www.test.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )


def post_ur_fifo() -> None:
    """Post to update request FIFO queue."""
    queue_url = get_sqs_queue_name("updaterequestfail")
    sqs_body = generate_sqs_body("abc@def.com")

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(),
    )


def post_to_change_event_dlq(context: Context) -> None:
    """Post to change event DLQ.

    Args:
        context (Context): Test context
    """
    queue_url = get_sqs_queue_name("changeevent")
    sqs_body = context.change_event

    SQS_CLIENT.send_message(
        QueueUrl=queue_url,
        MessageBody=dumps(sqs_body),
        MessageDeduplicationId=str(randint(10000, 99999)),
        MessageGroupId=str(randint(10000, 99999)),
        MessageAttributes=get_sqs_message_attributes(context.change_event["ODSCode"]),
    )


def get_sqs_message_attributes(odscode: str = "FW404") -> dict:
    """Generates a random set of message attributes for SQS.

    Args:
        odscode (str, optional): odscode to be added to message attributes. Defaults to "FW404".

    Returns:
        dict: message attributes
    """
    return {
        "correlation_id": {"DataType": "String", "StringValue": f"sqs-injection-id-{randint(0,1000)}"},
        "message_received": {"DataType": "Number", "StringValue": str(randint(1000, 5000))},
        "message_group_id": {"DataType": "Number", "StringValue": str(randint(1000, 5000))},
        "message_deduplication_id": {"DataType": "String", "StringValue": str(randint(1000, 99999))},
        "dynamo_record_id": {"DataType": "String", "StringValue": "78adf177e2cd469318e854e4e8068dd4"},
        "ods_code": {"DataType": "String", "StringValue": odscode},
        "error_msg": {"DataType": "String", "StringValue": "error_message"},
        "error_msg_http_code": {"DataType": "String", "StringValue": "404"},
        "sequence-number": {"DataType": "Number", "StringValue": str(time_ns())},
    }


def generate_sqs_body(website: str) -> dict:
    """Generate SQS body.

    Args:
        website (str): Website to update.

    Returns:
        dict: SQS body.
    """
    return {
        "reference": "14451_1657015307500997089_//www.test.com]",
        "system": "DoS Integration",
        "message": "DoS Integration CR. correlation-id: 14451_1657015307500997089_//www.test.com]",
        "replace_opening_dates_mode": True,
        "service_id": "22963",
        "changes": {"website": website},
    }
