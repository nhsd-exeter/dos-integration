from typing import Any, Dict
from aws_lambda_powertools import Logger, Tracer
from time import time_ns, strftime, gmtime
from os import environ
from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.utilities.typing import LambdaContext
from change_request import ChangeRequest
from common.middlewares import unhandled_exception_logging
from common.encryption import validate_event_is_signed
from common.utilities import extract_body

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@validate_event_is_signed
@logger.inject_lambda_context
@metric_scope
def lambda_handler(event: Dict[str, Any], context: LambdaContext, metrics) -> Dict:
    """Entrypoint handler for the event_sender lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """

    body = extract_body(event["body"])
    odscode = body["ods_code"]
    logger.append_keys(ods_code=odscode)
    dynamo_record_id = body["dynamo_record_id"]
    logger.append_keys(dynamo_record_id=dynamo_record_id)
    logger.set_correlation_id(body["correlation_id"])
    message_received = body["message_received"]
    s, ms = divmod(message_received, 1000)
    message_received_pretty = "%s.%03d" % (strftime("%Y-%m-%d %H:%M:%S", gmtime(s)), ms)
    logger.append_keys(message_received=message_received_pretty)
    logger.info(
        "Received change request",
        extra={"change_request": body["change_payload"]},
    )

    change_request = ChangeRequest(body["change_payload"])
    before = time_ns() // 1000000
    response = change_request.post_change_request()
    after = time_ns() // 1000000
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

    if response.ok:
        diff = after - message_received
        metrics.set_property("message", f"Recording change request latency of {diff}")
        metrics.put_metric("QueueToDoSLatency", diff, "Milliseconds")
    else:
        metrics.set_property("StatusCode", response.status_code)
        metrics.set_property("message", f"DoS API failed with status code {response.status_code}")
        metrics.put_metric("DoSApiFail", 1, "Count")
    return {"statusCode": response.status_code, "body": response.text}
