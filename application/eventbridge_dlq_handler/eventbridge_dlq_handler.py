from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body

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
    attributes = record.message_attributes
    message = record.body
    body = extract_body(message)
    logger.set_correlation_id(body["correlation_id"])
    logger.append_keys(dynamo_record_id=body["dynamo_record_id"])
    logger.append_keys(message_received=body["message_received"])
    logger.append_keys(ods_code=body["ods_code"])
    error_msg = attributes["ERROR_MESSAGE"]["stringValue"]
    attributes_error_msg_http_codes = [int(str) for str in error_msg.split() if str.isdigit()]
    logger.warning(
        "Eventbridge Dead Letter Queue Handler received event",
        extra={
            "report_key": DLQ_HANDLER_REPORT_ID,
            "dlq_event_attributes_error_msg": attributes["ERROR_MESSAGE"]["stringValue"],
            "dlq_event_attributes_error_msg_http_code": attributes_error_msg_http_codes[0],
            "dlq_event_attributes_error_code": attributes["ERROR_CODE"]["stringValue"],
            "dlq_event_attributes_rule_arn": attributes["RULE_ARN"]["stringValue"],
            "dlq_event_attributes_target_arn": attributes["TARGET_ARN"]["stringValue"],
            "dlq_event_body": body["change_payload"],
        },
    )
