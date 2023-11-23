from os import getenv

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.dynamodb import add_change_event_to_dynamodb
from common.middlewares import redact_staff_key_from_event, unhandled_exception_logging
from common.utilities import extract_body, get_sequence_number, get_sqs_msg_attribute, handle_sqs_msg_attributes

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
CHANGE_EVENT_DLQ_HANDLER_EVENT = "CHANGE_EVENT_DLQ_HANDLER_RECEIVED_EVENT"


@redact_staff_key_from_event()
@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@logger.inject_lambda_context(clear_state=True)
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:  # noqa: ARG001
    """Entrypoint handler for the change event dlq handler lambda.

    Messages are sent to the change event dlq handler lambda when a message
    fails in either the change event queue or holding queue

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object
    """
    record = next(event.records)
    handle_sqs_msg_attributes(record.message_attributes)
    body = extract_body(record.body)
    if "dynamo_record_id" not in record.body:
        # This is when a message comes from the change event queue
        attributes = handle_sqs_msg_attributes(record.message_attributes)
        correlation_id = get_sqs_msg_attribute(record.message_attributes, "correlation-id")
        logger.set_correlation_id(correlation_id)
        logger.append_keys(dynamo_record_id=get_sqs_msg_attribute(record.message_attributes, "dynamo_record_id"))
        logger.append_keys(message_received=get_sqs_msg_attribute(record.message_attributes, "message_received"))
        logger.append_keys(ods_code=get_sqs_msg_attribute(record.message_attributes, "ods_code"))
        change_event = body
        sequence_number = get_sequence_number(record)
    else:
        # This is when a message comes from the holding queue
        attributes = handle_sqs_msg_attributes(record.message_attributes)
        logger.info("Message received from holding queue", body=record.body)
        change_event = body["change_event"]
        correlation_id = body.get("correlation_id")
        logger.set_correlation_id(correlation_id)
        logger.append_keys(dynamo_record_id=body.get("dynamo_record_id"))
        logger.append_keys(message_received=body.get("message_received"))
        logger.append_keys(ods_code=change_event.get("ODSCode"))
        sequence_number = body.get("sequence_number")

    error_msg = attributes["error_msg"]
    logger.warning(
        "Change Event Dead Letter Queue Handler received event",
        report_key=CHANGE_EVENT_DLQ_HANDLER_EVENT,
        error_msg=f"Message Abandoned: {error_msg}",
        error_msg_http_code=attributes["error_msg_http_code"],
        payload=change_event,
        environment=getenv("ENVIRONMENT"),
        cloudwatch_metric_filter_matching_attribute="ChangeEventsDLQHandlerReceivedEvent",
    )
    sqs_timestamp = int(record.attributes["SentTimestamp"])
    add_change_event_to_dynamodb(change_event, sequence_number, sqs_timestamp)
