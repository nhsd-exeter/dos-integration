from os import getenv

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body, get_sqs_msg_attribute

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
DOS_DB_UPDATE_DLQ_HANDLER_EVENT = "DOS_DB_UPDATE_DLQ_HANDLER_RECEIVED_EVENT"


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@logger.inject_lambda_context(
    clear_state=True,
    correlation_id_path='Records[0].messageAttributes."correlation-id".stringValue',
)
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:  # noqa: ARG001
    """Entrypoint handler for the lambda.

    Args:
        event (SQSEvent): Lambda function invocation event (list of 1 SQS Message)
        context (LambdaContext): Lambda function context object
    """
    record = next(event.records)
    message = record.body
    body = extract_body(message)
    error_msg = get_sqs_msg_attribute(record.message_attributes, "error_msg")
    logger.warning(
        "DoS DB Update DLQ Handler hit",
        report_key=DOS_DB_UPDATE_DLQ_HANDLER_EVENT,
        error_msg=f"Message Abandoned: {error_msg}",
        error_msg_http_code=get_sqs_msg_attribute(record.message_attributes, "error_msg_http_code"),
        change_payload=body,
        dynamo_record_id=get_sqs_msg_attribute(record.message_attributes, "dynamo_record_id"),
        message_received=get_sqs_msg_attribute(record.message_attributes, "message_received"),
        ods_code=get_sqs_msg_attribute(record.message_attributes, "ods_code"),
        environment=getenv("ENVIRONMENT"),
        cloudwatch_metric_filter_matching_attribute="DoSDBUpdateDLQHandlerReceivedEvent",
    )
