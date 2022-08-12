from typing import Dict, List, Tuple

from aws_lambda_powertools.logging import Logger
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL

from .changes_to_dos import ChangesToDoS
from .service_histories import ServiceHistories
from common.dos import DoSService, get_specified_opening_times_from_db, get_standard_opening_times_from_db
from common.dos_db_connection import connect_to_dos_db, connect_to_dos_db_replica, query_dos_db
from common.opening_times import OpenPeriod, SpecifiedOpeningTime

logger = Logger(child=True)


def get_dos_service_and_history(service_id: int) -> Tuple[DoSService, ServiceHistories]:
    """Retrieves DoS Services from DoS database

    Args:
        service_id (str): Id of service to retrieve

    Returns:
        Tuple[DoSService, ServiceHistories]: Tuple of DoS service and service history

    """
    sql_query = (
        "SELECT s.id, uid, s.name, odscode, address, postcode, web, typeid,statusid, publicphone, publicname,"
        "st.name servicename FROM services s LEFT JOIN servicetypes st ON s.typeid = st.id "
        "WHERE s.id = %(SERVICE_ID)s"
    )
    query_vars = {"SERVICE_ID": service_id}
    # Connect to the DoS database replica (Read only)
    with connect_to_dos_db_replica() as connection:
        # Query the DoS database for the service
        cursor = query_dos_db(connection=connection, query=sql_query, vars=query_vars)
        rows: List[DictCursor] = cursor.fetchall()
        if len(rows) == 1:
            # Select first row (service) and create DoSService object
            service = DoSService(rows[0])
            logger.append_keys(service_name=service.name)
            logger.append_keys(service_uid=service.uid)
        elif not rows:
            raise ValueError(f"Service ID {service_id} not found")
        else:
            raise ValueError(f"Multiple services found for Service Id: {service_id}")
        # Set up remaining service data
        service.standard_opening_times = get_standard_opening_times_from_db(
            connection=connection, service_id=service_id
        )
        service.specified_opening_times = get_specified_opening_times_from_db(
            connection=connection, service_id=service_id
        )
        # Set up service history
        service_histories = ServiceHistories(service_id=service_id)
        service_histories.get_service_history_from_db(connection)
        service_histories.create_service_histories_entry()
        # Connection closed by context manager
    return service, service_histories


def update_dos_data(changes_to_dos: ChangesToDoS, service_id: int, service_histories: ServiceHistories) -> None:
    """Updates the DoS database with the changes to the service

    Args:
        changes_to_dos (ChangesToDoS): Changes to the dos service
        service_id (int): Id of service to update
        service_histories (ServiceHistories): Service history of the service
    """
    connection = None
    try:
        # Save all the changes to the DoS database with a single transaction
        with connect_to_dos_db() as connection:
            is_demographic_changes: bool = save_demographics_into_db(
                connection=connection, service_id=service_id, demographics_changes=changes_to_dos.demographic_changes
            )
            is_standard_opening_times_changes: bool = save_standard_opening_times_into_db(
                connection=connection,
                service_id=service_id,
                standard_opening_times_changes=changes_to_dos.standard_opening_times_changes,
            )
            is_specified_opening_times_changes: bool = save_specified_opening_times_into_db(
                connection=connection,
                service_id=service_id,
                is_changes=changes_to_dos.specified_opening_times_changes,
                specified_opening_times_changes=changes_to_dos.new_specified_opening_times,
            )
            # If there are any changes, update the service history and commit the changes to the database
            if any([is_demographic_changes, is_standard_opening_times_changes, is_specified_opening_times_changes]):
                service_histories.save_service_histories(connection=connection)
                connection.commit()
                logger.info(f"Updates successfully committed to the DoS database for service id {service_id}")
            else:
                logger.info(f"No changes to save for service id {service_id}")
    finally:
        # Close the connection even if an error occurs
        if connection:
            # Close without committing causes the transaction to be rolled back
            connection.close()


def save_demographics_into_db(connection: connection, service_id: int, demographics_changes: dict) -> bool:
    """Saves the demographic changes to the DoS database

    Args:
        connection (connection): Connection to the DoS database
        service_id (int): Id of service to update
        demographics_changes (dict): Demographic changes to save

    Returns:
        bool: True if any demographic changes were saved, False otherwise
    """
    if demographics_changes:
        # Update the service demographics
        logger.debug(f"Demographics changes found for service id {service_id}")
        query = SQL("""UPDATE services SET {} WHERE id = %(SERVICE_ID)s;""").format(
            SQL(", ".join(f"{key} = '{value}'" for key, value in demographics_changes.items()))
        )
        query_str = query.as_string(connection)

        cursor = query_dos_db(
            connection=connection,
            query=query_str,
            vars={"SERVICE_ID": service_id},
        )
        cursor.close()
        return True
    else:
        # No demographic changes found so no need to update the service
        logger.debug(f"No demographic changes found for service id {service_id}")
        return False


def save_standard_opening_times_into_db(
    connection: connection, service_id: int, standard_opening_times_changes: Dict[int, List[OpenPeriod]]
) -> bool:
    """Saves the standard opening times changes to the DoS database

    Args:
        connection (connection): Connection to the DoS database
        service_id (int): Id of the service to update
        standard_opening_times_changes (Dict[int, List[OpenPeriod]]): Changes to the standard opening times

    Returns:
        bool: True if changes were made to the database, False if no changes were made
    """
    if standard_opening_times_changes:
        logger.debug(f"Saving standard opening times changes for service id {service_id}")
        for dayid, opening_periods in standard_opening_times_changes.items():
            logger.debug(f"Deleting standard opening times for dayid: {dayid}")
            # Cascade delete the standard opening times in both
            # servicedayopenings table and servicedayopeningtimes table
            cursor = query_dos_db(
                connection=connection,
                query="""DELETE FROM servicedayopenings WHERE serviceid=%(SERVICE_ID)s AND dayid=%(DAY_ID)s""",
                vars={"SERVICE_ID": service_id, "DAY_ID": dayid},
            )
            cursor.close()
            if opening_periods != []:
                logger.debug(f"Saving standard opening times for dayid: {dayid}")
                cursor = query_dos_db(
                    connection=connection,
                    query=(
                        """INSERT INTO servicedayopenings (serviceid, dayid) """
                        """VALUES (%(SERVICE_ID)s, %(DAY_ID)s) RETURNING id"""
                    ),
                    vars={"SERVICE_ID": service_id, "DAY_ID": dayid},
                )
                # Get the id of the newly created servicedayopenings entry by using the RETURNING clause
                service_day_opening_id = cursor.fetchone()[0]
                cursor.close()

                open_period: OpenPeriod  # Type hint for the for loop
                for open_period in opening_periods:
                    logger.debug(f"Saving standard opening times period for dayid: {dayid}, period: {open_period}")
                    cursor = query_dos_db(
                        connection=connection,
                        query=(
                            """INSERT INTO servicedayopeningtimes (servicedayopeningid, starttime, endtime) """
                            """VALUES (%(SERVICE_DAY_OPENING_ID)s, %(OPEN_PERIOD_START)s, %(OPEN_PERIOD_END)s);"""
                        ),
                        vars={
                            "SERVICE_DAY_OPENING_ID": service_day_opening_id,
                            "OPEN_PERIOD_START": open_period.start,
                            "OPEN_PERIOD_END": open_period.end,
                        },
                    )
                    cursor.close()
            else:
                logger.debug(f"No standard opening times to add for {dayid}")
        return True
    else:
        logger.debug(f"No standard opening times changes to save for service id {service_id}")
        return False


def save_specified_opening_times_into_db(
    connection: connection,
    service_id: int,
    is_changes: bool,
    specified_opening_times_changes: List[SpecifiedOpeningTime],
) -> bool:
    """Saves the specified opening times changes to the DoS database

    Args:
        connection (connection): Connection to the DoS database
        service_id (int): Id of the service to update
        is_changes (bool): True if changes should be made to the database, False if no changes need to be made
        specified_opening_times_changes (List[SpecifiedOpeningTime]): Changes to the specified opening times

    Returns:
        bool: True if changes were made to the database, False if no changes were made
    """

    if is_changes:
        logger.debug(f"Deleting all specified opening times for service id {service_id}")
        # Cascade delete the standard opening times in both
        # servicedayopenings table and servicedayopeningtimes table
        cursor = query_dos_db(
            connection=connection,
            query=("""DELETE FROM servicespecifiedopeningdates WHERE serviceid=%(SERVICE_ID)s """),
            vars={"SERVICE_ID": service_id},
        )
        cursor.close()
        for specified_opening_times_day in specified_opening_times_changes:
            logger.debug(f"Saving specfied opening times for: {specified_opening_times_day}")
            cursor = query_dos_db(
                connection=connection,
                query=(
                    """INSERT INTO servicespecifiedopeningdates (date,serviceid) """
                    """VALUES (%(SPECIFIED_OPENING_TIMES_DATE)s,%(SERVICE_ID)s) RETURNING id;"""
                ),
                vars={"SPECIFIED_OPENING_TIMES_DATE": specified_opening_times_day.date, "SERVICE_ID": service_id},
            )
            # Get the id of the newly created servicedayopenings entry by using the RETURNING clause
            service_specified_opening_date_id = cursor.fetchone()[0]
            cursor.close()
            if specified_opening_times_day.is_open:
                # If the day is open, save the potentially mutiple opening times
                open_period: OpenPeriod  # Type hint for the for loop
                for open_period in specified_opening_times_day.open_periods:
                    logger.debug(
                        (
                            "Saving standard opening times period for dayid: "
                            f"{specified_opening_times_day.date}, period: {open_period}"
                        )
                    )
                    cursor = query_dos_db(
                        connection=connection,
                        query=(
                            """INSERT INTO servicespecifiedopeningtimes """
                            """(starttime, endtime, isclosed, servicespecifiedopeningdateid) """
                            """VALUES (%(OPEN_PERIOD_START)s, %(OPEN_PERIOD_END)s,"""
                            """%(IS_CLOSED)s,%(SERVICE_SPECIFIED_OPENING_DATE_ID)s);"""
                        ),
                        vars={
                            "OPEN_PERIOD_START": open_period.start,
                            "OPEN_PERIOD_END": open_period.end,
                            "IS_CLOSED": not specified_opening_times_day.is_open,
                            "SERVICE_SPECIFIED_OPENING_DATE_ID": service_specified_opening_date_id,
                        },
                    )
                    cursor.close()
            else:
                # If the day is closed, save the single closed all day times
                cursor = query_dos_db(
                    connection=connection,
                    query=(
                        """INSERT INTO servicespecifiedopeningtimes """
                        """(starttime, endtime, isclosed, servicespecifiedopeningdateid) """
                        """VALUES ('00:00:00', '00:00:00',"""
                        """%(IS_CLOSED)s,%(SERVICE_SPECIFIED_OPENING_DATE_ID)s);"""
                    ),
                    vars={
                        "IS_CLOSED": {not specified_opening_times_day.is_open},
                        "SERVICE_SPECIFIED_OPENING_DATE_ID": service_specified_opening_date_id,
                    },
                )
                cursor.close()

        return True
    else:
        logger.debug(f"No specified opening times changes to save for service id {service_id}")
        return False
