from json import dumps, loads
from os import environ
from typing import Any, Dict, Union

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

logger = Logger()


def is_val_none_or_empty(val: Any) -> bool:
    return not (val and not val.isspace())


def extract_body(body: str) -> Dict[str, Any]:
    """Extracts the event body from the lambda function invocation event

    Args:
        message_body (str): A JSON string body
    Returns:
        Dict[str, Any]: Message body as a dictionary
    """
    try:
        body = loads(body)
    except ValueError as e:
        raise ValueError("Change Event unable to be extracted") from e
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


def get_sqs_msg_attribute(msg_attributes: Dict[str, Any], key: str) -> Union[str, float, None]:
    attribute = msg_attributes.get(key)
    if attribute is None:
        return None
    data_type = attribute.get("dataType")
    if data_type == "String":
        return attribute.get("stringValue")
    if data_type == "Number":
        return float(attribute.get("stringValue"))


def handle_sqs_msg_attributes(msg_attributes: Dict[str, Any]) -> Dict[str, Any]:
    attributes = {"error_msg": "", "error_msg_http_code": ""}
    if msg_attributes is not None:
        if "error_msg_http_code" in msg_attributes:
            attributes["error_msg_http_code"] = msg_attributes["error_msg_http_code"]["stringValue"]
        if "error_msg" in msg_attributes:
            attributes["error_msg"] = msg_attributes["error_msg"]["stringValue"]

        return attributes


def remove_given_keys_from_dict_by_msg_limit(event: Dict[str, Any], keys: list, msg_limit: int = 10000):
    """Removing given keys from the dictionary if the dictonary size is morethan message limit
    Args:
        event Dict[str, Any]: Message body as a dictionary
        keys list: keys to be removed
        msg_limit int: message limit in char length
    Returns:
        Dict[str, Any]: Message body as a dictionary
    """
    msg_length = len(dumps(event).encode("utf-8"))
    if msg_length > msg_limit:
        return {k: v for k, v in event.items() if k not in keys}
    return event


@metric_scope
def add_metric(metric_name: str, metrics) -> None:  # type: ignore
    """Adds a failure metric to the custom metrics collection"""
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.put_metric(metric_name, 1, "Count")
    metrics.put_metric("UpdateRequestFailed", 1, "Count")
    metrics.set_dimensions({"ENV": environ["ENV"]})
