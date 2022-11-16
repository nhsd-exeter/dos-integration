from json import dumps
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from common.dos import (
    get_specified_opening_times_from_db,
    get_standard_opening_times_from_db,
    SpecifiedOpeningTime,
    VALID_STATUS_ID,
)
from common.dos_db_connection import connect_to_dos_db, query_dos_db
from common.middlewares import unhandled_exception_logging
from common.service_type import get_valid_service_types

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
        return True
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
    elif request["type"] == "change_event_demographics":
        odscode = request.get("odscode")
        organisation_type_id = request.get("organisation_type_id")
        if odscode is None or organisation_type_id is None:
            raise ValueError(f"Missing values: odscode: {odscode}, organisation_type_id: {organisation_type_id}")
        type_id_query = get_valid_service_types_equals_string(organisation_type_id)
        db_columns = (
            "id",
            "name",
            "odscode",
            "address",
            "postcode",
            "web",
            "typeid",
            "statusid",
            "publicphone",
            "publicname",
        )
        query = (
            f"SELECT {', '.join(db_columns)} "
            f"FROM services WHERE odscode like %(ODSCODE)s AND typeid {type_id_query} "
            "AND statusid = %(VALID_STATUS_ID)s AND odscode IS NOT NULL"
        )
        query_vars = {
            "ODSCODE": f"{odscode}%",
            "VALID_STATUS_ID": VALID_STATUS_ID,
        }
        query_results = run_query(query, query_vars)
        if len(query_results) <= 0:
            raise ValueError(f"No matching services for odscode {odscode}")
        query_results = query_results[0]
        result = dict(zip(db_columns, query_results))
        #comment to push again
        return result
    else:
        raise ValueError("Unsupported request")


def run_query(query, query_vars) -> list:
    logger.info("Running query", extra={"query": query})
    with connect_to_dos_db() as connection:
        cursor = query_dos_db(connection=connection, query=query, vars=query_vars)
        query_result = cursor.fetchall()
        connection.commit()
        cursor.close()
    return query_result


def get_valid_service_types_equals_string(organisation_type_id: str) -> str:
    """Gets a query string for to match valid dos service type id/ids

    Args:
        organisation_type_id (str): Organsation type id

    Returns:
        str: Equals string to include in query
    """
    valid_service_types: list = get_valid_service_types(organisation_type_id)
    if len(valid_service_types) > 1:
        valid_service_types = tuple(valid_service_types)
        type_id_query = f"IN {valid_service_types}"
    else:
        type_id_query = f"= {valid_service_types[0]}"
    return type_id_query
