from logging import Logger
from os import environ
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.utilities.typing import LambdaContext

from ..logger import import_logger_from_file, set_log_level, setup_logger

FILE_PATH = "application.common.logger"


@patch(f"{FILE_PATH}.LogFilter")
@patch(f"{FILE_PATH}.set_log_level")
@patch(f"{FILE_PATH}.getLogger")
@patch(f"{FILE_PATH}.import_logger_from_file")
def test_setup_logger(mock_import_logger_from_file, mock_getLogger, mock_set_log_level, mock_LogFilter):
    # Arrange
    logger = MagicMock()
    mock_getLogger.return_value = logger
    event = {}
    lambda_context = LambdaContext()
    # Act
    call_setup_logger(event, lambda_context)
    # Assert
    mock_import_logger_from_file.assert_called_with()
    mock_getLogger.assert_called_with("lambda")
    mock_set_log_level.assert_called_with(logger)
    mock_LogFilter.assert_called_with(lambda_context)


@patch(f"{FILE_PATH}.fileConfig")
@patch(f"{FILE_PATH}.path")
def test_import_logger_from_file(mock_path, mock_fileConfig):
    # Arrange
    test_path = "test/path/to/file.txt"
    mock_path.join.return_value = test_path
    # Act
    import_logger_from_file()
    # Assert
    mock_fileConfig.assert_called_with(test_path)


def test_set_log_level() -> None:
    # Arrange
    logger = Logger("my-logger1")
    environ["LOG_LEVEL"] = "WARNING"
    # Act
    logger = set_log_level(logger)
    # Assert
    assert logger.level == 30
    # Clean up
    del environ["LOG_LEVEL"]


def test_set_log_level_no_log_level() -> None:
    # Arrange
    logger = Logger("my-logger2")
    # Act
    logger = set_log_level(logger)
    # Assert
    assert logger.level == 20


@setup_logger
def call_setup_logger(event: Dict[str, Any], context: LambdaContext) -> None:
    return {"status": 200, "message": "Lambda is complete"}
