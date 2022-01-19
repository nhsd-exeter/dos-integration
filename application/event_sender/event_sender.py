from typing import Any, Dict

from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Logger
from time import time_ns, strftime, gmtime
from os import environ
from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.utilities.typing import LambdaContext
from change_request import ChangeRequest
from common.middlewares import unhandled_exception_logging
from common.utilities import extract_body

tracer = Tracer()
logger = Logger()


@tracer.capture_lambda_handler()
@unhandled_exception_logging
@logger.inject_lambda_context
@metric_scope
def lambda_handler(event: Dict[str, Any], context: LambdaContext, metrics) -> Dict:
    """Entrypoint handler for the event_sender lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    body = extract_body(event["body"])
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
    response = change_request.post_change_request()
    if (response.status_code == 200):
        now_ms = time_ns() // 1000000
        metrics.put_dimensions({"ENV": environ["ENV"]})
        metrics.put_metric("ProcessingLatency", now_ms - message_received, "Milliseconds")
    return {"statusCode": response.status_code, "body": response.text}

