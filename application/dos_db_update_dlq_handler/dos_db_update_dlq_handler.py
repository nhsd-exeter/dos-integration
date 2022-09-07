from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.constants import DLQ_HANDLER_REPORT_ID
from common.middlewares import unhandled_exception_logging
from common.utilities import add_metric, extract_body, get_sqs_msg_attribute

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@logger.inject_lambda_context()
@metric_scope
def lambda_handler(event: SQSEvent, context: LambdaContext, metrics) -> None:
    """Entrypoint handler for the lambda

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object
    """
    record = next(event.records)
    message = record.body
    body = extract_body(message)
    correlation_id = get_sqs_msg_attribute(record.message_attributes, "correlation_id")
    error_msg = get_sqs_msg_attribute(record.message_attributes, "error_msg")
    logger.set_correlation_id(correlation_id)
    logger.append_keys(dynamo_record_id=get_sqs_msg_attribute(record.message_attributes, "dynamo_record_id"))
    logger.append_keys(message_received=get_sqs_msg_attribute(record.message_attributes, "message_received"))
    logger.append_keys(ods_code=get_sqs_msg_attribute(record.message_attributes, "ods_code"))
    logger.warning(
        "DoS DB Update DLQ Handler hit",
        extra={
            "report_key": DLQ_HANDLER_REPORT_ID,
            "error_msg": f"Message Abandoned: {error_msg}",
            "error_msg_http_code": get_sqs_msg_attribute(record.message_attributes, "error_msg_http_code"),
            "change_payload": body,
        },
    )
    metrics.set_namespace("AWS/SQS")
    metrics.set_property("level", "WARNING")
    metrics.set_property("message", error_msg)
    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.put_metric("NumberOfMessagesReceived", 1, "Count")
    add_metric("ServiceUpdateFailed")
