from os import environ, getenv
from unittest.mock import MagicMock, patch

from ..dos_db_connection import _get_db_connection, _set_db_connection, disconnect_dos_db, query_dos_db

FILE_PATH = "application.common.dos_db_connection"


@patch(f"{FILE_PATH}.get_secret")
@patch("psycopg2.connect")
def test_query_dos_db(mock_connect, mock_get_secret):
    # Arrange
    environ["DB_SERVER"] = server = "test.db"
    environ["DB_PORT"] = port = "5432"
    environ["DB_NAME"] = db_name = "my-db"
    environ["DB_SCHEMA"] = db_schema = "db_schema"
    environ["DB_USER_NAME"] = db_user = "my-user"
    environ["DB_SECRET_NAME"] = "my_secret_name"
    environ["DB_SECRET_KEY"] = "my_secret_key"
    mock_get_secret.return_value = {environ["DB_SECRET_KEY"]: "my-password"}
    db_password = mock_get_secret.return_value[environ["DB_SECRET_KEY"]]
    query = "SELECT * FROM my_table"
    vars = None
    # Act
    query_dos_db(query, vars)
    # Assert
    mock_connect.assert_called_with(
        host=server,
        port=port,
        dbname=db_name,
        user=db_user,
        password=db_password,
        connect_timeout=30,
        options=f"-c search_path=dbo,{db_schema}",
        application_name=f"DI-Application <psycopg2> tid={getenv('_X_AMZN_TRACE_ID', default='<NO-TRACE-ID>')}",
    )
    mock_get_secret.assert_called_once_with(environ["DB_SECRET_NAME"])
    assert _get_db_connection() is not None
    # Clean up
    del environ["DB_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_USER_NAME"]
    del environ["DB_SECRET_NAME"]
    del environ["DB_SECRET_KEY"]


def test_disconnect_dos_db():
    # Arrange
    mock_db_connection = MagicMock()
    _set_db_connection(mock_db_connection)
    # Act
    disconnect_dos_db()
    # Assert
    mock_db_connection.close.assert_called()
