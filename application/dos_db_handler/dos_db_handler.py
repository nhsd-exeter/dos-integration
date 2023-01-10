from json import dumps
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.dos import get_specified_opening_times_from_db, get_standard_opening_times_from_db, SpecifiedOpeningTime
from common.dos_db_connection import connect_to_dos_db, query_dos_db
from common.middlewares import unhandled_exception_logging

logger = Logger()


@unhandled_exception_logging()
@logger.inject_lambda_context(clear_state=True)
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> str:
    """Entrypoint handler for the lambda

    WARNING: This lambda is for TESTING PURPOSES ONLY.
    It is not intended to be used in production.

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object
    """
    request = event
    result = None
    generic_queries = ["write", "read", "insert"]

    if request["type"] in generic_queries:
        query = request["query"]
        query_vars = request["query_vars"]

        result = run_query(query, query_vars)

    if request["type"] == "write":
        # returns a single value (typically id)
        return dumps(result, default=str)[0][0]
    elif request["type"] == "read":
        # returns all values
        return dumps(result, default=str)
    elif request["type"] == "insert":
        # returns no values
        return "True"
    elif request["type"] == "change_event_standard_opening_times":
        service_id = request.get("service_id")
        if service_id is None:
            raise ValueError("Missing service_id")
        with connect_to_dos_db() as connection:
            standard_opening_times = get_standard_opening_times_from_db(connection=connection, service_id=service_id)
            result = standard_opening_times.export_test_format()
            return result
    elif request["type"] == "change_event_specified_opening_times":
        service_id = request.get("service_id")
        if service_id is None:
            raise ValueError("Missing service_id")
        with connect_to_dos_db() as connection:
            specified_opening_times = get_specified_opening_times_from_db(connection=connection, service_id=service_id)
            result = SpecifiedOpeningTime.export_test_format_list(specified_opening_times)
            return result
    else:
        # add comment
        raise ValueError("Unsupported request")


def run_query(query, query_vars) -> list:
    logger.info("Running query", extra={"query": query})
    with connect_to_dos_db() as connection:
        cursor = query_dos_db(connection=connection, query=query, vars=query_vars)
        query_result = cursor.fetchall()
        connection.commit()
        cursor.close()
    return query_result
