from aws_lambda_powertools.logging import Logger
from psycopg.rows import DictRow

from .service_histories import ServiceHistories
from common.dos import (
    DoSService,
    get_specified_opening_times_from_db,
    get_standard_opening_times_from_db,
    has_blood_pressure,
    has_contraception,
    has_palliative_care,
)
from common.dos_db_connection import connect_to_db_writer, query_dos_db

logger = Logger(child=True)


def get_dos_service_and_history(service_id: int) -> tuple[DoSService, ServiceHistories]:
    """Retrieves DoS Services from DoS database.

    Args:
        service_id (str): Id of service to retrieve

    Returns:
        Tuple[DoSService, ServiceHistories]: Tuple of DoS service and service history

    """
    sql_query = (
        "SELECT s.id, uid, s.name, odscode, address, town, postcode, web, typeid, statusid, ss.name status_name, "
        "publicphone, publicname, st.name service_type_name, easting, northing, latitude, longitude FROM services s "
        "LEFT JOIN servicetypes st ON s.typeid = st.id LEFT JOIN servicestatuses ss on s.statusid = ss.id "
        "WHERE s.id = %(SERVICE_ID)s"
    )
    query_vars = {"SERVICE_ID": service_id}
    # Connect to the DoS database
    with connect_to_db_writer() as connection:
        # Query the DoS database for the service
        cursor = query_dos_db(connection=connection, query=sql_query, query_vars=query_vars)
        rows: list[DictRow] = cursor.fetchall()
        if len(rows) == 1:
            # Select first row (service) and create DoSService object
            service = DoSService(rows[0])
            logger.append_keys(service_name=service.name)
            logger.append_keys(service_uid=service.uid)
            logger.append_keys(type_id=service.typeid)
        elif not rows:
            msg = f"Service ID {service_id} not found"
            raise ValueError(msg)
        else:
            msg = f"Multiple services found for Service Id: {service_id}"
            raise ValueError(msg)
        # Set up remaining service data
        service.standard_opening_times = get_standard_opening_times_from_db(
            connection=connection,
            service_id=service_id,
        )
        service.specified_opening_times = get_specified_opening_times_from_db(
            connection=connection,
            service_id=service_id,
        )
        # Set up palliative care flag
        service.palliative_care = has_palliative_care(service=service, connection=connection)
        # Set up blood pressure flag
        service.blood_pressure = has_blood_pressure(service=service)
        # Set up contraception flag
        service.contraception = has_contraception(service=service)
        # Set up service history
        service_histories = ServiceHistories(service_id=service_id)
        service_histories.get_service_history_from_db(connection)
        service_histories.create_service_histories_entry()
        # Connection closed by context manager
    return service, service_histories
