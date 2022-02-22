from hashlib import sha256
from json import dumps
from os import environ
from time import gmtime, strftime, time_ns
from typing import Dict

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from change_request import ChangeRequest
from common.dynamodb import put_circuit_is_open
from common.middlewares import unhandled_exception_logging
from common.types import ChangeRequestQueueItem

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@logger.inject_lambda_context
@metric_scope
def lambda_handler(event: ChangeRequestQueueItem, context: LambdaContext, metrics) -> Dict:
    """Entrypoint handler for the event_sender lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """

    sqs = client("sqs")
    if not event["is_health_check"]:
        odscode = event["metadata"]["ods_code"]
        logger.append_keys(ods_code=odscode)
        dynamo_record_id = event["metadata"]["dynamo_record_id"]
        logger.append_keys(dynamo_record_id=dynamo_record_id)
        logger.set_correlation_id(event["metadata"]["correlation_id"])
        message_received = event["metadata"]["message_received"]
        s, ms = divmod(message_received, 1000)
        message_received_pretty = "%s.%03d" % (strftime("%Y-%m-%d %H:%M:%S", gmtime(s)), ms)
        logger.append_keys(message_received=message_received_pretty)
        logger.info(
            "Received change request",
            extra={"change_request": event["change_request"]},
        )
    change_request = ChangeRequest(event["change_request"])
    if event["is_health_check"]:
        change_request = ChangeRequest({})

    before = time_ns() // 1000000
    response = change_request.post_change_request()
    after = time_ns() // 1000000
    if not event["is_health_check"]:
        metrics.set_namespace("UEC-DOS-INT")
        metrics.set_property("level", "INFO")
        metrics.set_property("function_name", context.function_name)
        metrics.set_property("message_received", message_received_pretty)

        metrics.set_property("ods_code", odscode)
        metrics.set_property("correlation_id", logger.get_correlation_id())
        metrics.set_property("dynamo_record_id", dynamo_record_id)
        metrics.set_dimensions({"ENV": environ["ENV"]})
        dos_time = after - before
        metrics.put_metric("DosApiLatency", dos_time, "Milliseconds")

    if response.ok and not event["is_health_check"]:
        diff = after - message_received
        metrics.set_property("message", f"Recording change request latency of {diff}")
        metrics.put_metric("QueueToDoSLatency", diff, "Milliseconds")
        # remove from the queue to avoid reprocessing
        sqs.delete_message(QueueUrl=environ["CR_QUEUE_URL"], ReceiptHandle=event["recipient_id"])

    else:
        if event["is_health_check"] and response.status_code in [400, 200, 201]:
            logger.info("Circuit fixed - closing the circuit")
            put_circuit_is_open(environ["CIRCUIT"], False)
        else:
            # TODO: The current DoS Api returns 500 when it should return 400, this isn't ideal
            # as it means we will circuit break unnecessarily and this could happen repeatidly until
            # the message is DLQ'd - 5 times, if we can fix that then these message could be sent to the dlq
            # and deleted to avoid circuit breaking and even replaying when we know it will fail again
            if response.status_code >= 500 or response.status_code == 429:
                logger.info("Potentially recoverable breaking circuit to retry shortly")
                put_circuit_is_open(environ["CIRCUIT"], True)
            elif 400 <= response.status_code < 500:
                logger.info("Permanent error sending to DLQ, Not retrying")
                hashed_payload = sha256(str(event["change_request"]).encode()).hexdigest()
                sqs.send_message(
                    QueueUrl=environ["CR_DLQ_URL"],
                    MessageBody=dumps(event["change_request"]),
                    MessageDeduplicationId=f"{time_ns()}-{hashed_payload}",
                    MessageGroupId=odscode,
                    MessageAttributes={
                        "correlation_id": {"DataType": "String", "StringValue": logger.get_correlation_id()},
                        "message_received": {"DataType": "Number", "StringValue": str(message_received)},
                        "dynamo_record_id": {"DataType": "String", "StringValue": dynamo_record_id},
                        "ods_code": {"DataType": "String", "StringValue": odscode},
                        "error_msg": {"DataType": "String", "StringValue": response.text},
                        "error_msg_http_code": {"DataType": "String", "StringValue": response.status_code},
                    },
                )
                sqs.delete_message(QueueUrl=environ["CR_QUEUE_URL"], ReceiptHandle=event["recipient_id"])
            metrics.set_property("StatusCode", response.status_code)
            metrics.set_property("message", f"DoS API failed with status code {response.status_code}")
            metrics.put_metric("DoSApiFail", 1, "Count")
    return {"statusCode": response.status_code, "body": response.text}
