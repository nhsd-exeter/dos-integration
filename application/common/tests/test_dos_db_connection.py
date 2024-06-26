from os import environ
from unittest.mock import MagicMock, patch

from psycopg.rows import dict_row

from application.common.dos_db_connection import (
    connect_to_db_reader,
    connect_to_db_writer,
    connection_to_db,
    query_dos_db,
)

FILE_PATH = "application.common.dos_db_connection"

DB_WRITER_SERVER = "test.db"
DB_READER_SERVER = "test.db"
DB_PORT = "5432"
DB_NAME = "my-db"
DB_SCHEMA = "db_schema"
DB_USER = "my-user"
DB_PASSWORD = "my-password"


@patch(f"{FILE_PATH}.connection_to_db")
@patch(f"{FILE_PATH}.get_secret")
def test_connect_to_db_reader(mock_get_secret: MagicMock, mock_connection_to_db: MagicMock) -> None:
    # Arrange
    mock_get_secret.return_value = {"DB_READER_SECRET_KEY": DB_PASSWORD}
    environ["DB_READER_SECRET_NAME"] = "my_secret_name"
    environ["DB_READER_SERVER"] = DB_READER_SERVER
    environ["DB_PORT"] = DB_PORT
    environ["DB_NAME"] = DB_NAME
    environ["DB_SCHEMA"] = DB_SCHEMA
    environ["DB_READ_ONLY_USER_NAME"] = DB_USER
    environ["DB_READER_SECRET_KEY"] = "DB_READER_SECRET_KEY"
    environ["DB_SECRET"] = DB_PASSWORD
    # Act
    with connect_to_db_reader() as db_connection:
        # Assert
        assert db_connection is not None
    mock_connection_to_db.assert_called_with(
        server=DB_READER_SERVER,
        port=DB_PORT,
        db_name=DB_NAME,
        db_schema=DB_SCHEMA,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
    )
    # Clean up
    del environ["DB_READER_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_READ_ONLY_USER_NAME"]
    del environ["DB_READER_SECRET_KEY"]
    del environ["DB_READER_SECRET_NAME"]


@patch(f"{FILE_PATH}.connection_to_db")
@patch(f"{FILE_PATH}.get_secret")
def test_connect_to_db_writer(mock_get_secret: MagicMock, mock_connection_to_db: MagicMock) -> None:
    # Arrange
    mock_get_secret.return_value = {"DB_WRITER_SECRET_KEY": DB_PASSWORD}
    environ["DB_WRITER_SECRET_NAME"] = "my_secret_name"
    environ["DB_WRITER_SERVER"] = DB_WRITER_SERVER
    environ["DB_PORT"] = DB_PORT
    environ["DB_NAME"] = DB_NAME
    environ["DB_SCHEMA"] = DB_SCHEMA
    environ["DB_READ_AND_WRITE_USER_NAME"] = DB_USER
    environ["DB_WRITER_SECRET_KEY"] = "DB_WRITER_SECRET_KEY"
    # Act
    with connect_to_db_writer() as db_connection:
        # Assert
        assert db_connection is not None
    mock_connection_to_db.assert_called_once_with(
        server=DB_WRITER_SERVER,
        port=DB_PORT,
        db_name=DB_NAME,
        db_schema=DB_SCHEMA,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
    )
    # Clean up
    del environ["DB_WRITER_SECRET_NAME"]
    del environ["DB_WRITER_SERVER"]
    del environ["DB_PORT"]
    del environ["DB_NAME"]
    del environ["DB_SCHEMA"]
    del environ["DB_READ_AND_WRITE_USER_NAME"]
    del environ["DB_WRITER_SECRET_KEY"]


@patch(f"{FILE_PATH}.connect")
def test_connection_to_db(mock_connect: MagicMock) -> None:
    # Act
    connection_to_db(
        server=DB_WRITER_SERVER,
        port=DB_PORT,
        db_name=DB_NAME,
        db_schema=DB_SCHEMA,
        db_user=DB_USER,
        db_password=DB_PASSWORD,
    )
    # Assert
    mock_connect.assert_called_with(
        host=DB_WRITER_SERVER,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=2,
        options=f"-c search_path=dbo,{DB_SCHEMA}",
        application_name="DOS INTEGRATION <psycopg>",
    )


def test_query_dos_db() -> None:
    # Arrange
    query = "SELECT * FROM my_table"
    connection = MagicMock()
    # Act
    result = query_dos_db(connection, query)
    # Assert
    assert result == connection.cursor.return_value
    connection.cursor.assert_called_once_with(row_factory=dict_row)
    connection.cursor.return_value.execute.assert_called_once_with(query=query, params=None)
