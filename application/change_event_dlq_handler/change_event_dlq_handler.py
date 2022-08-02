from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import event_source, SQSEvent
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.constants import FIFO_DLQ_HANDLER_REPORT_ID
from common.dynamodb import add_change_request_to_dynamodb
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body, get_sequence_number, get_sqs_msg_attribute, handle_sqs_msg_attributes

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
    attributes = handle_sqs_msg_attributes(record.message_attributes)
    correlation_id = get_sqs_msg_attribute(record.message_attributes, "correlation-id")
    logger.set_correlation_id(correlation_id)
    logger.append_keys(dynamo_record_id=get_sqs_msg_attribute(record.message_attributes, "dynamo_record_id"))
    logger.append_keys(message_received=get_sqs_msg_attribute(record.message_attributes, "message_received"))
    logger.append_keys(ods_code=get_sqs_msg_attribute(record.message_attributes, "ods_code"))
    message = record.body
    body = extract_body(message)
    error_msg = attributes["error_msg"]
    logger.warning(
        "FIFO Dead Letter Queue Handler received event",
        extra={
            "report_key": FIFO_DLQ_HANDLER_REPORT_ID,
            "error_msg": f"Message Abandoned: {error_msg}",
            "error_msg_http_code": attributes["error_msg_http_code"],
            "payload": body,
        },
    )
    metrics.set_namespace("AWS/SQS")
    metrics.set_property("level", "WARNING")
    metrics.set_property("message", error_msg)
    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.put_metric("NumberOfMessagesReceived", 1, "Count")

    sqs_timestamp = int(record.attributes["SentTimestamp"])
    sequence_number = get_sequence_number(record)
    add_change_request_to_dynamodb(body, sequence_number, sqs_timestamp)
