from dataclasses import dataclass
from datetime import datetime
from json import dump, loads
from os import remove
from time import time_ns
from typing import List, Optional

from aws_lambda_powertools.logging import Logger
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from pytz import timezone

from .service_update_logging import ServiceUpdateLogger
from common.constants import DI_CHANGE_ITEMS, DOS_INTEGRATION_USER_NAME
from common.dos_db_connection import connect_to_dos_db, query_dos_db
from common.s3 import put_email_to_s3
from common.types import EmailFile

logger = Logger(child=True)


@dataclass(repr=True)
class PendingChange:
    """A class representing a pending change from the DoS database with useful information about the change"""

    id: str  # Id of the pending change from the change table
    value: str  # Value of the pending change as a JSON string
    creatorsname: str  # User name of the user who made the change
    email: str  # Email address of the user who made the change
    typeid: str  # Type id of the service
    name: str  # Name of the service
    uid: str  # Uid of the service

    def __init__(self, db_cursor_row: dict) -> None:
        """Sets the attributes of this object to those found in the db row
        Args:
            db_cursor_row (dict): row from db as key/val pairs
        """
        for row_key, row_value in db_cursor_row.items():
            setattr(self, row_key, row_value)

    def is_valid(self) -> bool:
        """Checks if the pending change is valid

        Returns:
            bool: True if the pending change is valid, False otherwise
        """
        try:
            value_dict = loads(self.value)
            changes = value_dict["new"]
            is_types_valid = [True if change in DI_CHANGE_ITEMS else False for change in changes.keys()]
            return all(is_types_valid)
        except Exception:
            logger.exception(f"Invalid JSON: {self.value}")
            return False


def check_and_remove_pending_dos_changes(service_id: str) -> None:
    """Checks for pending changes in DoS and removes them if they exist

    Args:
        service_id (str): The ID of the service to check
    """
    with connect_to_dos_db() as connection:
        pending_changes = get_pending_changes(connection=connection, service_id=service_id)
        if pending_changes != [] and pending_changes is not None:
            logger.info("Pending Changes to be rejected", extra={"pending_changes": pending_changes})
            reject_pending_changes(connection=connection, pending_changes=pending_changes)
            connection.commit()
            log_rejected_changes(pending_changes)
            send_rejection_emails(pending_changes)
            logger.info("All pending changes rejected and emails sent")
        else:
            logger.info("No valid pending changes found")


def get_pending_changes(connection: connection, service_id: str) -> Optional[List[PendingChange]]:
    """Gets pending changes for a service ID

    Args:
        connection (connection): The connection to the DoS database
        service_id (str): The ID of the service to check

    Returns:
        Optional[List[Dict[str, Any]]]: A list of pending changes or None if there are no pending changes
    """
    # Get pending changes
    sql_query = (
        "SELECT c.id, c.value, c.creatorsname, u.email, s.typeid, s.name, s.uid "
        "FROM changes c LEFT JOIN users u ON u.username = c.creatorsname "
        "LEFT JOIN services s ON s.id = c.serviceid "
        "WHERE serviceid=%(SERVICE_ID)s AND approvestatus='PENDING'"
    )
    query_vars = {"SERVICE_ID": service_id}
    cursor = query_dos_db(connection=connection, query=sql_query, vars=query_vars)
    rows: List[DictCursor] = cursor.fetchall()
    logger.debug("rows", extra={"rows": rows})
    cursor.close()
    if len(rows) >= 1:
        logger.info(f"Pending changes found for Service ID {service_id}")
        pending_changes: List[PendingChange] = []
        for row in rows:
            pending_change = PendingChange(row)
            logger.info(f"Pending change found: {pending_change}", extra={"pending_change": pending_change})
            if pending_change.is_valid():
                logger.debug(f"Pending change is valid: {pending_change.id}", extra={"pending_change": pending_change})
                pending_changes.append(pending_change)
            else:
                logger.info(f"Pending change {pending_change.id} is invalid", extra={"pending_change": pending_change})
        return pending_changes
    elif not rows:
        return None
    else:
        raise ValueError(f"Multiple services found for Service Id: {service_id}")


def reject_pending_changes(connection: connection, pending_changes: List[PendingChange]) -> None:
    """Rejects pending changes from the database

    Args:
        connection (connection): The connection to the DoS database
        pending_changes (List[PendingChange]): The pending change to reject
    """
    conditions = (
        f"id='{pending_changes[0].id}'"
        if len(pending_changes) == 1
        else f"""id in ({",".join(f"'{change.id}'" for change in pending_changes)})"""
    )
    sql_query = (  # nosec - SQL Injection is prevented by the query only using data from DoS DB
        "UPDATE changes SET approvestatus='REJECTED',modifiedtimestamp=%(TIMESTAMP)s, modifiersname=%(USER_NAME)s"
        f""" WHERE {conditions}"""
    )
    query_vars = {
        "USER_NAME": DOS_INTEGRATION_USER_NAME,
        "TIMESTAMP": datetime.now(timezone("Europe/London")),
    }
    cursor = query_dos_db(connection=connection, query=sql_query, vars=query_vars)
    cursor.close()
    logger.info("Rejected pending change/s", extra={"pending_changes": pending_changes})


def log_rejected_changes(pending_changes: List[PendingChange]) -> None:
    """Logs the rejected changes

    Args:
        pending_changes (List[PendingChange]): The pending changes to log
    """
    for pending_change in pending_changes:
        ServiceUpdateLogger(
            service_uid=pending_change.uid,
            service_name=pending_change.name,
            type_id=pending_change.typeid,
        ).log_rejected_change(pending_change.id)


def send_rejection_emails(pending_changes: List[PendingChange]) -> None:
    """Sends rejection emails to the users who created the pending changes

    Args:
        pending_changes (List[PendingChange]): The pending changes to send rejection emails for
    """
    for pending_change in pending_changes:
        file = EmailFile(
            correlation_id=logger.get_correlation_id(),
            recipient_email_address=pending_change.email,
            email_body=build_change_rejection_email_contents(pending_change),
            email_subject="Your DoS Change has been rejected",
        )
        logger.debug("Create email file", extra={"file": file})
        email_file_filepath = "/tmp/rejection-email.json"  # nosec - File is created in a temporary directory in
        with open(email_file_filepath, "w+") as email_file:
            dump(file, email_file)
            email_file.close()
        logger.debug("Email file created")
        put_email_to_s3(email_file_filepath, f"rejection-emails/rejection-email-{time_ns()}.json")
        remove(email_file_filepath)


def build_change_rejection_email_contents(pending_change: PendingChange) -> str:
    """Builds the contents of the change rejection email

    Args:
        pending_change (PendingChange): The pending change to build the email for

    Returns:
        str: The contents of the email
    """
    with open("service_sync/rejection-email.html", "r") as email_template:
        file_contents = email_template.read()
        email_template.close()
    email_correlation_id = f"{pending_change.uid}-{time_ns()}"
    file_contents = file_contents.replace("{{InitiatorName}}", pending_change.creatorsname)
    file_contents = file_contents.replace("{{ServiceName}}", pending_change.name)
    file_contents = file_contents.replace("{{ServiceUid}}", pending_change.uid)
    file_contents = file_contents.replace("{{EmailCorrelationId}}", email_correlation_id)
    logger.info("Email Correlation Id", extra={"email_correlation_id": email_correlation_id})
    json_value = loads(pending_change.value)
    for change_key, value in json_value["new"].items():
        # Add a new change row to the table in the email
        row = TABLE_ROW
        row = row.replace("{{change_key}}", change_key)
        row = row.replace("{{previous}}", str(value.get("previous")))
        row = row.replace("{{new}}", str(value.get("data")))
        file_contents = file_contents.replace("{{row}}", row)
        logger.debug("Added row to table in email", extra={"row": row})
    # Remove the placeholder row
    file_contents = file_contents.replace("{{row}}", " ")
    # Remove the \n characters from the HTML
    file_contents = file_contents.replace("\n", " ")
    return file_contents


TABLE_ROW: str = """
        <tr>
            <td>{{change_key}}</td>
            <td>{{previous}}</td>
            <td>{{new}}</td>
        </tr>
        {{row}}
    """
