from os import environ, getenv
from typing import Union

import psycopg2
from aws_lambda_powertools import Logger
from common.secretsmanager import get_secret
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

logger = Logger(child=True)
db_connection = None


def _connect_dos_db() -> connection:
    """Creates a new connection to the DoS DB and returns the connection object

    warning: Do not use. Should only be used by query_dos_db() func
    """
    db_secret = get_secret(environ["DB_SECRET_NAME"])
    server = environ["DB_SERVER"]
    port = environ["DB_PORT"]
    db_name = environ["DB_NAME"]
    db_schema = environ["DB_SCHEMA"]
    db_user = environ["DB_USER_NAME"]
    db_password = db_secret[environ["DB_SECRET_KEY"]]
    trace_id = getenv("_X_AMZN_TRACE_ID", default="<NO-TRACE-ID>")

    logger.debug(f"Attempting connection to database '{server}'")
    logger.debug(f"host={server}, port={port}, dbname={db_name}, schema={db_schema} user={db_user}")

    db = psycopg2.connect(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=30,
        options=f"-c search_path=dbo,{db_schema}",
        application_name=f"DI-Application <psycopg2> tid={trace_id}",
    )

    return db


def disconnect_dos_db() -> None:
    """Closes the DoS database connection if it exists and is open"""
    global db_connection
    if db_connection is not None:
        try:
            db_connection.close()
            logger.info("The DoS database connection was closed.")
        except Exception as e:
            logger.exception(f"There was an exception while trying to close DoS database connection: {e}")


def query_dos_db(query: str, vars: Union[tuple, dict, None] = None) -> DictCursor:
    """Queries the dos database with given sql command and returns the resulting cursor object"""

    # Check if new connection needed.
    global db_connection
    if db_connection is None or db_connection.closed != 0:
        db_connection = _connect_dos_db()
    else:
        logger.info("Using existing open database connection.")

    c = db_connection.cursor(cursor_factory=DictCursor)

    query_string_log = f"Running SQL command: {c.mogrify(query, vars)}"
    if len(query_string_log) > 1000:
        query_string_log = f"{query_string_log[:490]}...       ...{query_string_log[-490:]}"
    logger.info(query_string_log)

    c.execute(query, vars)
    return c


def _set_db_connection(value):
    global db_connection
    db_connection = value


def _get_db_connection():
    return db_connection
