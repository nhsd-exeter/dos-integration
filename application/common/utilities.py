from json import dumps, loads
from os import environ
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

from common.types import UpdateRequest

logger = Logger()


def is_val_none_or_empty(val: Any) -> bool:  # noqa: ANN401
    """Checks if the value is None or empty.

    Args:
        val (Any): Value to check

    Returns:
        bool: True if the value is None or empty, False otherwise
    """
    return not (val and not val.isspace())


def extract_body(body: str) -> dict[str, Any] | UpdateRequest:
    """Extracts the event body from the lambda function invocation event.

    Args:
        body (str): Lambda function invocation event body

    Returns:
        Dict[str, Any] | UpdateRequest: Message body as a dictionary
    """
    try:
        return loads(body)
    except ValueError as e:
        msg = "Change Event unable to be extracted"
        raise ValueError(msg) from e


def json_str_body(body: dict[str, Any]) -> str:
    """Encode a Dict event body from the lambda function invocation event into a JSON string.

    Args:
        body (Dict[str, Any]): A Dict body

    Returns:
        (str): A JSON string body
    """
    try:
        return dumps(body)
    except ValueError as e:
        msg = "Dict Change Event body cannot be converted to a JSON string"
        raise ValueError(msg) from e


def get_sequence_number(record: SQSRecord) -> int | None:
    """Gets the sequence number from the SQS record sent by NHS UK.

    Args:
        record (SQSRecord): SQS record

    Returns:
        Optional[int]: Sequence number of the message or None if not present.
    """
    seq_num_str = record.message_attributes.get("sequence-number", {}).get("stringValue")
    return None if seq_num_str is None else int(seq_num_str)


def get_sqs_msg_attribute(msg_attributes: dict[str, Any], key: str) -> str | float | None:
    """Gets the value of the given key from the SQS message attributes.

    Args:
        msg_attributes (dict[str, Any]): Message attributes
        key (str): Key to get the value for

    Returns:
        str | float | None: Value of the given key or None if not present.
    """
    attribute = msg_attributes.get(key)
    if attribute is None:
        return None
    data_type = attribute.get("dataType")
    if data_type == "String":
        return attribute.get("stringValue")
    return float(attribute.get("stringValue")) if data_type == "Number" else None


def handle_sqs_msg_attributes(msg_attributes: dict[str, Any]) -> dict[str, Any] | None:
    """Extracts the error message and error message http code from the SQS message attributes.

    Args:
        msg_attributes (dict[str, Any]): Message attributes

    Returns:
        dict[str, Any]: Dictionary with error message and error message http code or None if not present.
    """
    if msg_attributes is not None:
        attributes = {"error_msg": "", "error_msg_http_code": ""}
        if "error_msg_http_code" in msg_attributes:
            attributes["error_msg_http_code"] = msg_attributes["error_msg_http_code"]["stringValue"]
        if "error_msg" in msg_attributes:
            attributes["error_msg"] = msg_attributes["error_msg"]["stringValue"]

        return attributes
    return None


def remove_given_keys_from_dict_by_msg_limit(
    event: dict[str, Any],
    keys: list,
    msg_limit: int = 10000,
) -> dict[str, Any]:
    """Removing given keys from the dictionary if the dictionary size is more than message limit.

    Args:
        event (Dict[str, Any]): Message body as a dictionary
        keys (list): List of keys to be removed from the dictionary
        msg_limit (int): Message limit in characters

    Returns:
        Dict[str, Any]: Message body as a dictionary.
    """
    msg_length = len(dumps(event).encode("utf-8"))
    if msg_length > msg_limit:
        return {k: v for k, v in event.items() if k not in keys}
    return event


@metric_scope
def add_metric(metric_name: str, metrics: Any) -> None:  # noqa: ANN401
    """Adds a metric to the custom metrics collection.

    Args:
        metric_name (str): Name of the metric to be added to CloudWatch
        metrics (Class): Metrics class
    """
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.put_metric(metric_name, 1, "Count")
    metrics.set_dimensions({"ENV": environ["ENV"]})
