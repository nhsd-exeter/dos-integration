from json import dumps
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
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

tracer = Tracer()
logger = Logger()


@unhandled_exception_logging()
@tracer.capture_lambda_handler()
@logger.inject_lambda_context()
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
    if request["type"] == "get_pharmacy_odscodes":
        type_id_query = get_valid_service_types_equals_string("PHA")
        query = (
            f"SELECT LEFT(odscode, 5) FROM services WHERE typeid {type_id_query} "
            f"AND statusid = {VALID_STATUS_ID} AND odscode IS NOT NULL"
        )
        result = run_query(query, None)
    elif request["type"] == "get_taken_odscodes":
        query = "SELECT LEFT(odscode, 5) FROM services"
        result = run_query(query, None)
    elif request["type"] == "get_pharmacy_odscodes_with_contacts":
        type_id_query = get_valid_service_types_equals_string("PHA")
        query = (
            f"SELECT LEFT(odscode,5) FROM services WHERE typeid {type_id_query} AND LENGTH(odscode) > 4 "
            f"AND statusid = {VALID_STATUS_ID} AND odscode IS NOT NULL AND RIGHT(address, 1) != '$' "
            "AND publicphone IS NOT NULL AND web IS NOT NULL GROUP BY LEFT(odscode,5) HAVING COUNT(odscode) = 1"
        )
        result = run_query(query, None)
    elif request["type"] == "get_single_service_pharmacy_odscode":
        type_id_query = get_valid_service_types_equals_string("PHA")
        query = (
            f"SELECT LEFT(odscode,5) FROM services WHERE typeid {type_id_query} "
            f"AND statusid = {VALID_STATUS_ID} AND odscode IS NOT NULL AND RIGHT(address, 1) != '$' "
            "AND LENGTH(odscode) > 4 GROUP BY LEFT(odscode,5) HAVING COUNT(odscode) = 1"
        )
        result = run_query(query, None)
    elif request["type"] == "get_dentist_odscodes":
        type_id_query = get_valid_service_types_equals_string("Dentist")
        query = (
            f"SELECT odscode FROM services WHERE typeid {type_id_query} "
            f"AND statusid = {VALID_STATUS_ID} AND odscode IS NOT NULL AND LENGTH(odscode) = 6 AND LEFT(odscode, 1)='V'"
        )
        result = run_query(query, None)
    elif request["type"] == "get_services_count":
        cid = request.get("odscode")
        if cid is None:
            raise ValueError("Missing odscode")
        query = f"SELECT count(*) FROM services where odscode like '{cid}%'"
        result = run_query(query, None)
    elif request["type"] == "get_changes":
        cid = request.get("correlation_id")
        if cid is None:
            raise ValueError("Missing correlation id")
        query = f"SELECT value from changes where externalref = '{cid}'"
        result = run_query(query, None)
    elif request["type"] == "get_service_id":
        odscode = request.get("odscode")
        if odscode is None:
            raise ValueError("Missing correlation id")
        type_id_query = get_valid_service_types_equals_string("PHA")
        query = (
            f"SELECT id FROM services WHERE typeid {type_id_query} "
            f"AND statusid = {VALID_STATUS_ID} AND odscode like '{odscode}%' LIMIT 1"
        )
        result = run_query(query, None)
    elif request["type"] == "get_approver_status":
        cid = request.get("correlation_id")
        if cid is None:
            raise ValueError("Missing correlation id")
        query = f"SELECT modifiedtimestamp from changes where approvestatus = 'COMPLETE' and externalref = '{cid}'"
        result = run_query(query, None)
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
    # This is the one being called
    elif request["type"] == "change_event_standard_opening_times":
        service_id = request.get("service_id")
        if service_id is None:
            raise ValueError("Missing service_id")
        with connect_to_dos_db() as connection:
            standard_opening_times = get_standard_opening_times_from_db(connection=connection, service_id=service_id)
            result = standard_opening_times.export_test_format()
    elif request["type"] == "change_event_specified_opening_times":
        service_id = request.get("service_id")
        if service_id is None:
            raise ValueError("Missing service_id")
        with connect_to_dos_db() as connection:
            specified_opening_times = get_specified_opening_times_from_db(connection=connection, service_id=service_id)
            result = SpecifiedOpeningTime.export_test_format_list(specified_opening_times)
    elif request["type"] == "get_service_table_field":
        service_id = request.get("service_id")
        field = request.get("field")
        if service_id is None or field is None:
            raise ValueError("Missing data in get_service_table_field request")
        result = run_query(
            query=f"SELECT {field} FROM services WHERE id = %(SERVICE_ID)s",
            query_vars={"SERVICE_ID": service_id},
        )
    elif request["type"] == "get_service_history":
        service_id = request.get("service_id")
        if service_id is None:
            raise ValueError("Missing data in get_service_history request")
        result = run_query(
            query="SELECT history FROM servicehistories WHERE serviceid = %(SERVICE_ID)s",
            query_vars={"SERVICE_ID": service_id},
        )
    elif request["type"] == "get_services_table_location":
        service_id = request.get("service_id")
        if service_id is None:
            raise ValueError("Missing data in get_services_table_values request")
        result = run_query(
            query=(
                "SELECT town, postcode, easting, northing, latitude, longitude "
                "FROM services WHERE id = %(SERVICE_ID)s"
            ),
            query_vars={"SERVICE_ID": service_id},
        )
    elif request["type"] == "get_locations_table_values":
        postcode = request.get("postcode")
        if postcode is None:
            raise ValueError("Missing data in get_locations_table_values")
        result = run_query(
            query=(
                "SELECT postaltown, postcode, easting, northing, latitude, longitude "
                "FROM locations WHERE postcode = %(POSTCODE)s"
            ),
            query_vars={"POSTCODE": postcode},
        )
    elif request["type"] == "create_changes_entry_for_service":
        service_id = request.get("service_id")
        unique_id = request.get("unique_id")
        if service_id is None:
            raise ValueError("Missing service id for changes table")
        json_obj = {
            "new": {
                "cmstelephoneno": {"changetype": "add", "data": "abcd", "area": "demographic", "previous": "0"},
                "cmsurl": {"changetype": "add", "data": "abcd", "area": "demographic", "previous": ""},
            },
            "initiator": {"userid": "admin", "timestamp": "2022-09-01 13:35:41"},
            "approver": {"userid": "admin", "timestamp": "01-09-2022 13:35:41"},
        }

        values = (
            f"66301ABC-D3A4-0B8F-D7F8-F286INT{unique_id}",
            "PENDING",
            "modify",
            "Test Admin",
            "Test Duplicate",
            "DoS Region",
            dumps(json_obj),
            "2022-09-06 11:00:00.000 +0100",
            "Test Admin",
            str(service_id),
        )

        query = (
            "INSERT INTO pathwaysdos.changes VALUES (id, approvestatus, \"type\", initiatorname, servicename, "
            "servicetype, value, createdtimestamp, creatorsname, serviceid) "
            "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
        )
        result = run_query(query, values)
    else:
        raise ValueError("Unsupported request")
    return dumps(result, default=str)


def run_query(query, query_vars) -> list:
    logger.info("Running query", extra={"query": query})
    with connect_to_dos_db() as connection:
        cursor = query_dos_db(connection=connection, query=query, vars=query_vars)
        query_result = cursor.fetchall()
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
