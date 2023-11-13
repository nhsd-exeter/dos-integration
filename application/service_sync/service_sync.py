from os import environ
from time import time_ns
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client

from .data_processing.check_for_change import compare_nhs_uk_and_dos_data
from .data_processing.get_data import get_dos_service_and_history
from .data_processing.update_dos import update_dos_data
from .reject_pending_changes.pending_changes import check_and_remove_pending_dos_changes
from common.middlewares import unhandled_exception_logging
from common.nhs import NHSEntity
from common.types import UpdateRequest
from common.utilities import add_metric, extract_body

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@logger.inject_lambda_context(clear_state=True)
@event_source(data_class=SQSEvent)
def lambda_handler(event: SQSEvent, context: LambdaContext) -> None:  # noqa: ARG001
    """Entrypoint handler for the service_sync lambda.

    Args:
        event (SQSEvent): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    try:
        record: SQSRecord = next(event.records)
        update_request: UpdateRequest = extract_body(record.body)
        logger.set_correlation_id(str(record.message_attributes.get("correlation_id", {}).get("stringValue")))
        logger.append_keys(
            ods_code=update_request["change_event"].get("ODSCode"),
            service_id=update_request["service_id"],
        )
        service_id: str = update_request["service_id"]
        check_and_remove_pending_dos_changes(service_id)
        # Set up NHS UK Service
        change_event: dict[str, Any] = update_request["change_event"]
        nhs_entity = NHSEntity(change_event)
        # Get current DoS state
        dos_service, service_histories = get_dos_service_and_history(service_id=int(service_id))
        # Compare NHS UK and DoS data
        changes_to_dos = compare_nhs_uk_and_dos_data(
            dos_service=dos_service,
            nhs_entity=nhs_entity,
            service_histories=service_histories,
        )
        # Update Service History with changes to be made
        service_histories = changes_to_dos.service_histories
        # Update DoS data
        update_dos_data(changes_to_dos=changes_to_dos, service_id=int(service_id), service_histories=service_histories)
        # Delete the message from the queue
        remove_sqs_message_from_queue(receipt_handle=record.receipt_handle)
        # Log custom metrics
        add_success_metric(
            message_received=int(record.message_attributes.get("message_received", {}).get("stringValue")),
        )
        add_metric("UpdateRequestSuccess")
        add_metric("ServiceUpdateSuccess")
    except Exception:
        add_metric("UpdateRequestFailed")
        logger.exception("Error processing change event")


def remove_sqs_message_from_queue(receipt_handle: str) -> None:
    """Removes the SQS message from the queue.

    Args:
        receipt_handle (str): The SQS message receipt handle
    """
    sqs = client("sqs")
    sqs.delete_message(QueueUrl=environ["UPDATE_REQUEST_QUEUE_URL"], ReceiptHandle=receipt_handle)
    logger.info("Removed SQS message from queue", receipt_handle=receipt_handle)


@metric_scope
def add_success_metric(message_received: int, metrics: Any) -> None:  # noqa: ANN401
    """Adds a success metric to the custom metrics collection.

    Args:
        message_received (int): The time the message was received in milliseconds
        metrics (Any): The custom metrics collection
    """
    after = time_ns() // 1000000
    diff = after - message_received
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("message", f"Recording change event latency of {diff}")
    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.set_property("level", "WARNING")
    metrics.put_metric("QueueToDoSLatency", diff, "Milliseconds")
