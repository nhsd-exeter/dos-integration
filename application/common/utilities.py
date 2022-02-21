from json import loads
from typing import Any, Dict, Union
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord


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


def get_sqs_msg_attribute(msg_attributes: Dict[str, Any], key: str) -> Union[str, float]:
    attribute = msg_attributes.get(key)
    if attribute is None:
        return None
    data_type = attribute.get("dataType")
    if data_type == "String":
        return attribute.get("stringValue")
    if data_type == "Number":
        return float(attribute.get("stringValue"))


def handle_sqs_msg_attributes(msg_attributes: Dict[str, Any]) -> Dict[str, Any]:
    attributes = {
        "error_msg": "",
        "error_msg_http_code": None,
        "error_code": "",
        "rule_arn": "",
        "target_arn": "",
        "change_payload": "",
    }
    if msg_attributes is not None:
        if "ERROR_MESSAGE" in msg_attributes:
            error_msg = msg_attributes["ERROR_MESSAGE"]["stringValue"]
            attributes["error_msg"] = error_msg
            error_msg_http_codes = [int(str) for str in error_msg.split() if str.isdigit()]
            if len(error_msg_http_codes) > 0:
                attributes["error_msg_http_code"] = error_msg_http_codes[0]

        if "ERROR_CODE" in msg_attributes:
            attributes["error_code"] = msg_attributes["ERROR_CODE"]["stringValue"]

        if "RULE_ARN" in msg_attributes:
            attributes["rule_arn"] = msg_attributes["RULE_ARN"]["stringValue"]

        if "TARGET_ARN" in msg_attributes:
            attributes["target_arn"] = msg_attributes["TARGET_ARN"]["stringValue"]

        return attributes
