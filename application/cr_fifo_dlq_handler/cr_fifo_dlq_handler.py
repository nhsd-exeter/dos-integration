from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body, get_sqs_msg_attribute


TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
DLQ_HANDLER_REPORT_ID = "CR_DLQ_HANDLER_RECEIVED_EVENT"


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
    message = record.body
    body = extract_body(message)
    correlation_id = get_sqs_msg_attribute(record.message_attributes, "correlation_id")
    logger.set_correlation_id(correlation_id)
    logger.append_keys(dynamo_record_id=get_sqs_msg_attribute(record.message_attributes, "dynamo_record_id"))
    logger.append_keys(message_received=get_sqs_msg_attribute(record.message_attributes, "message_received"))
    logger.append_keys(ods_code=get_sqs_msg_attribute(record.message_attributes, "ods_code"))
    logger.warning(
        "Change Request DLQ Handler hit",
        extra={
            "report_key": DLQ_HANDLER_REPORT_ID,
            "error_msg": f"Message Abandoned: {get_sqs_msg_attribute(record.message_attributes,'error_msg')}",
            "error_msg_http_code": get_sqs_msg_attribute(record.message_attributes, "error_msg_http_code"),
            "change_payload": body,
        },
    )
