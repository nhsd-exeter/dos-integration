from contextlib import contextmanager
from os import environ
from time import time_ns
from typing import Any, Dict, Generator, Optional

from aws_lambda_powertools.logging import Logger
from psycopg2 import connect
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

from common.secretsmanager import get_secret

logger = Logger(child=True)
db_connection = None


@contextmanager
def connect_to_dos_db_replica() -> Generator[connection, None, None]:
    """Creates a new connection to the DoS DB Replica

    Yields:
        Generator[connection, None, None]: Connection to the database
    """
    # Use AWS secret values, or failing that check env for DB password
    if "DB_REPLICA_SECRET_NAME" in environ and "DB_REPLICA_SECRET_KEY" in environ:
        db_secret = get_secret(environ["DB_REPLICA_SECRET_NAME"])
        db_password = db_secret[environ["DB_REPLICA_SECRET_KEY"]]
    else:
        db_password = environ["DB_SECRET"]

    # Before the context manager is entered, the connection is created
    db_connection = connection_to_db(
        server=environ["DB_REPLICA_SERVER"],
        port=environ["DB_PORT"],
        db_name=environ["DB_NAME"],
        db_schema=environ["DB_SCHEMA"],
        db_user=environ["DB_READ_ONLY_USER_NAME"],
        db_password=db_password
    )
    # Yield the connection object to the context manager
    yield db_connection
    # After the context manager is exited, the connection is closed
    db_connection.close()


@contextmanager
def connect_to_dos_db() -> Generator[connection, None, None]:
    """Creates a new connection to the DoS DB

    Yields:
        Generator[connection, None, None]: Connection to the database
    """
    # Before the context manager is entered, the connection is created
    db_secret = get_secret(environ["DB_SECRET_NAME"])
    db_connection = connection_to_db(
        server=environ["DB_SERVER"],
        port=environ["DB_PORT"],
        db_name=environ["DB_NAME"],
        db_schema=environ["DB_SCHEMA"],
        db_user=environ["DB_READ_AND_WRITE_USER_NAME"],
        db_password=db_secret[environ["DB_SECRET_KEY"]],
    )
    # Yield the connection object to the context manager
    yield db_connection
    # After the context manager is exited, the connection is closed
    db_connection.close()


def connection_to_db(
    server: str, port: str, db_name: str, db_schema: str, db_user: str, db_password: str
) -> connection:
    """Creates a new connection to a database

    Args:
        server (str): Database server to connect to
        port (str): Database port to connect to
        db_name (str): Database name to connect to
        db_schema (str): Database schema to connect to
        db_user (str): Database user to connect as
        db_password (str): Database password for the user

    Returns:
        connection: Connection to the database
    """
    logger.info(f"Attempting connection to database '{server}'")
    logger.debug(f"host={server}, port={port}, dbname={db_name}, schema={db_schema}, user={db_user}")
    return connect(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=5,
        options=f"-c search_path=dbo,{db_schema}",
        application_name="DOS INTEGRATION <psycopg2>",
    )


def query_dos_db(
        connection: connection,
        query: str,
        vars: Optional[Dict[str, Any]] = None,
        log_vars: bool = True) -> DictCursor:
    """Queries the database given in the connection object

    Args:
        connection (connection): Connection to the database
        query (str): Query to execute
        vars (Optional[Dict[str, Any]], optional): Variables to use in the query. Defaults to None.

    Returns:
        DictCursor: Cursor to the query results
    """
    cursor = connection.cursor(cursor_factory=DictCursor)

    logger.debug("Query to execute", extra={"query": query, "vars": vars if log_vars else "Vars have been redacted."})
    query_string_log = cursor.mogrify(query, vars) if log_vars else query
    if len(query_string_log) > 1000:
        query_string_log = f"{query_string_log[:490]}...  ...{query_string_log[-490:]}"
    logger.info(f"Running SQL command: {query_string_log}")

    time_start = time_ns() // 1000000
    cursor.execute(query, vars)
    logger.info(f"DoS DB query completed in {(time_ns() // 1000000) - time_start}ms")
    return cursor
