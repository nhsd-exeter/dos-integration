from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body
from typing import Any, Dict

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
DLQ_HANDLER_REPORT_ID = "EVENTBRIDGE_DLQ_HANDLER_RECEIVED_EVENT"


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@logger.inject_lambda_context()
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:
    """Entrypoint handler for the lambda

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object
    """
    record = next(event.records)
    attributes = handle_sqs_msg_attributes(record.message_attributes)
    message = record.body
    body = extract_body(message)
    logger.set_correlation_id(body["correlation_id"])
    logger.append_keys(dynamo_record_id=body["dynamo_record_id"])
    logger.append_keys(message_received=body["message_received"])
    logger.append_keys(ods_code=body["ods_code"])
    logger.warning(
        "Eventbridge Dead Letter Queue Handler received event",
        extra={
            "report_key": DLQ_HANDLER_REPORT_ID,
            "error_msg": attributes["error_msg"],
            "error_msg_http_code": attributes["error_msg_http_code"],
            "error_code": attributes["error_code"],
            "rule_arn": attributes["rule_arn"],
            "target_arn": attributes["target_arn"],
            "change_payload": body["change_payload"],
        },
    )


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
