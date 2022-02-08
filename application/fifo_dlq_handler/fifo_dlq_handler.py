from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.dynamodb import add_change_request_to_dynamodb
from common.middlewares import set_correlation_id, unhandled_exception_logging
from common.utilities import extract_body, get_sequence_number, handle_sqs_msg_attributes

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
FIFO_DLQ_HANDLER_REPORT_ID = "FIFO_DLQ_HANDLER_RECEIVED_EVENT"


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@set_correlation_id()
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
    logger.warning(
        "FIFO Dead Letter Queue Handler received event",
        extra={
            "report_key": FIFO_DLQ_HANDLER_REPORT_ID,
            "error_msg": attributes["error_msg"],
            "error_msg_http_code": attributes["error_msg_http_code"],
            "error_code": attributes["error_code"],
            "rule_arn": attributes["rule_arn"],
            "target_arn": attributes["target_arn"],
            "payload": body,
        },
    )

    sqs_timestamp = int(record.attributes["SentTimestamp"])
    sequence_number = get_sequence_number(record)
    add_change_request_to_dynamodb(body, sequence_number, sqs_timestamp)
