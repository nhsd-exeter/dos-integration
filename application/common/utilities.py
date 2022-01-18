from json import dumps, loads
from os import environ, getenv
from typing import Any, Dict, Union
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from boto3 import client


logger = Logger()


def extract_body(body: str) -> Dict[str, Any]:
    """Extracts the event body from the lambda function invocation event

    Args:
        message_body (str): A JSON string body
    Returns:
        Dict[str, Any]: Message body as a dictionary
    """
    try:
        body = loads(body)
    except Exception:
        logger.exception("Change Event unable to be extracted")
        raise
    return body


def get_sequence_number(record: SQSRecord) -> Union[int, None]:
    """Gets the sequence number from the SQS record
    Args:
        record (SQSRecord): SQS record
    Returns:
        Optional[int]: Sequence number of the message or None if not present
    """
    seq_num_str = record.message_attributes.get("sequence-number", {}).get("stringValue")
    return None if seq_num_str is None else int(seq_num_str)
