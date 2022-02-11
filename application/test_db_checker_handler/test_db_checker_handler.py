from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.middlewares import unhandled_exception_logging
from common.dos_db_connection import query_dos_db
from json import dumps
from typing import Dict, Any


tracer = Tracer()
logger = Logger()
VALID_SERVICE_TYPES = {13, 131, 132, 134, 137}
VALID_STATUS_ID = 1


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@logger.inject_lambda_context()
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> str:
    """Entrypoint handler for the lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    request = event
    query = ""
    if request["type"] == "ods":
        query = (
            f"SELECT LEFT(odscode, 5) FROM services WHERE typeid IN {tuple(VALID_SERVICE_TYPES)} "
            f"AND statusid = '{VALID_STATUS_ID}' AND odscode IS NOT NULL"
        )
    elif request["type"] == "change":
        cid = request.get("correlation_id")
        if cid is not None:
            query = f"SELECT value from changes where externalref = '{cid}'"
        else:
            raise ValueError("Missing correlation id")
    else:
        raise ValueError("Unsupported request")
    cursor = query_dos_db(query)
    result = cursor.fetchall()
    return dumps(result)
