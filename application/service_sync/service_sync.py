from os import environ
from time import time_ns
from typing import Any, Dict

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client

from .compare_data import compare_nhs_uk_and_dos_data
from .dos_data import get_dos_service_and_history, run_db_health_check, update_dos_data
from .pending_changes import check_and_remove_pending_dos_changes
from common.dynamodb import put_circuit_is_open
from common.middlewares import unhandled_exception_logging
from common.nhs import NHSEntity
from common.types import UpdateRequestMetadata, UpdateRequestQueueItem
from common.utilities import add_metric

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@logger.inject_lambda_context(clear_state=True)
def lambda_handler(event: UpdateRequestQueueItem, context: LambdaContext) -> None:
    """Entrypoint handler for the service_sync lambda

    Args:
        event (UpdateRequestQueueItem): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    logger.append_keys(health_check=event["is_health_check"])
    try:
        if event["is_health_check"]:
            run_db_health_check()
            return
        set_up_logging(event)
        # Not a health check, so process the update request
        service_id: int = event["update_request"]["service_id"]
        check_and_remove_pending_dos_changes(service_id)
        # Set up NHS UK Service
        change_event: Dict[str, Any] = event["update_request"]["change_event"]
        nhs_entity = NHSEntity(change_event)
        # Get current DoS state
        dos_service, service_histories = get_dos_service_and_history(service_id=service_id)
        # Compare NHS UK and DoS data
        changes_to_dos = compare_nhs_uk_and_dos_data(
            dos_service=dos_service,
            nhs_entity=nhs_entity,
            service_histories=service_histories,
        )
        # Update Service History with changes to be made
        service_histories = changes_to_dos.service_histories
        # Update DoS data
        update_dos_data(changes_to_dos=changes_to_dos, service_id=service_id, service_histories=service_histories)
        # Delete the message from the queue
        remove_sqs_message_from_queue(event=event)
        # Log custom metrics
        add_success_metric(event=event)  # type: ignore
        add_metric("UpdateRequestSuccess")
        add_metric("ServiceUpdateSuccess")
    except Exception:
        put_circuit_is_open(environ["CIRCUIT"], True)
        add_metric("UpdateRequestFailed")  # type: ignore
        logger.exception("Error processing change event")


def set_up_logging(event: UpdateRequestQueueItem) -> None:
    logger.set_correlation_id(event["metadata"]["correlation_id"])
    logger.append_keys(
        ods_code=event["update_request"]["change_event"].get("ODSCode"),
        service_id=event["update_request"]["service_id"],
    )


def remove_sqs_message_from_queue(event: UpdateRequestQueueItem) -> None:
    """Removes the SQS message from the queue

    Args:
        event (UpdateRequestQueueItem): Lambda function invocation event
    """
    sqs = client("sqs")
    sqs.delete_message(QueueUrl=environ["UPDATE_REQUEST_QUEUE_URL"], ReceiptHandle=event["recipient_id"])
    logger.info("Removed SQS message from queue", extra={"receipt_handle": event["recipient_id"]})


@metric_scope
def add_success_metric(event: UpdateRequestQueueItem, metrics) -> None:  # type: ignore
    """Adds a success metric to the custom metrics collection

    Args:
        event (UpdateRequestQueueItem): Lambda function invocation event
    """
    after = time_ns() // 1000000
    metadata: UpdateRequestMetadata = event["metadata"]
    message_received = metadata["message_received"]
    diff = after - message_received
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "INFO")
    metrics.set_property("message", f"Recording change event latency of {diff}")
    metrics.put_metric("QueueToDoSLatency", diff, "Milliseconds")
    metrics.set_dimensions({"ENV": environ["ENV"]})
