from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.data_classes import SQSEvent, event_source
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.middlewares import unhandled_exception_logging
from common.dos import query_dos_db, VALID_SERVICE_TYPES, VALID_STATUS_ID
from json import dumps
from typing import Dict

TTL = 157680000  # int((365*5)*24*60*60) . 5 years in seconds
tracer = Tracer()
logger = Logger()
DLQ_HANDLER_REPORT_ID = "EVENTBRIDGE_DLQ_HANDLER_RECEIVED_EVENT"


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@event_source(data_class=SQSEvent)
@logger.inject_lambda_context()
def lambda_handler(event: Dict, context: LambdaContext) -> str:
    """Entrypoint handler for the lambda

    Args:
        event (str): query to run against the db
        context (LambdaContext): Lambda function context object
    """
    request = event
    query = ""
    if request["type"] == "ods":
        query = (
            f"SELECT LEFT(odscode, 5) FROM services WHERE typeid IN {tuple(VALID_SERVICE_TYPES)} "
            f"AND statusid = '{VALID_STATUS_ID}'"
        )
    elif request["type"] == "change":
        cid = request.get("correlation_id")
        if cid is not None:
            query = f"SELECT value from changes where externalref = '{cid}'"
        else:
            raise ValueError("Missing correlation id")
    else:
        raise ValueError("Unsupported request")

    result = query_dos_db(query)
    return dumps(result)
