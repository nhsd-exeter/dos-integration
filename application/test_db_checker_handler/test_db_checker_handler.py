from json import dumps
from typing import Any, Dict

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.dos import (
    VALID_SERVICE_TYPES,
    VALID_STATUS_ID,
    SpecifiedOpeningTime,
    get_matching_dos_services,
    get_specified_opening_times_from_db,
    get_standard_opening_times_from_db,
)
from common.dos_db_connection import query_dos_db
from common.middlewares import unhandled_exception_logging

tracer = Tracer()
logger = Logger()


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
    query = None
    query_vars = None
    result = None
    if request["type"] == "get_odscodes":
        query = (
            f"SELECT LEFT(odscode, 5) FROM services WHERE typeid IN {tuple(VALID_SERVICE_TYPES)} "
            f"AND statusid = '{VALID_STATUS_ID}' AND odscode IS NOT NULL"
        )
    elif request["type"] == "get_single_service_odscode":
        query = (
            f"SELECT LEFT(odscode,5) AS ODS_5 FROM services WHERE typeid IN {tuple(VALID_SERVICE_TYPES)} "
            f"AND statusid = '{VALID_STATUS_ID}' AND odscode IS NOT NULL AND odscode != ''"
            "AND LENGTH(LEFT(odscode,5)) = 5 GROUP BY left(odscode,5) having count(left(odscode,5)) = 1"
        )
    elif request["type"] == "get_changes":
        cid = request.get("correlation_id")
        if cid is not None:
            query = f"SELECT value from changes where externalref = '{cid}'"
        else:
            raise ValueError("Missing correlation id")
    elif request["type"] == "change_event_demographics":
        odscode = request.get("odscode")
        if odscode is not None:
            services = get_matching_dos_services(odscode)
            if len(services) > 0:
                service = services[0].__dict__
                result = service
            else:
                raise ValueError(f"No matching services for ods {odscode}")
        else:
            raise ValueError("Missing odscode")
    elif request["type"] == "change_event_standard_opening_times":
        service_id = request.get("service_id")
        if service_id is not None:
            standard_opening_times = get_standard_opening_times_from_db(service_id)
            result = standard_opening_times.export_cr_format()
        else:
            raise ValueError("Missing service_id")
    elif request["type"] == "change_event_specified_opening_times":
        service_id = request.get("service_id")
        if service_id is not None:
            specified_opening_times = get_specified_opening_times_from_db(service_id)
            result = SpecifiedOpeningTime.export_cr_format_list(specified_opening_times)
        else:
            raise ValueError("Missing service_id")
    else:
        raise ValueError("Unsupported request")

    if query is not None:
        cursor = query_dos_db(query, query_vars)
        result = cursor.fetchall()
        cursor.close()

    print(result)
    return dumps(result, default=str)
