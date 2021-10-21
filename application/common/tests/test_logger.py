from logging import Logger
from os import environ

from ..logger import set_log_level


def test_setup_logger():
    pass
    # Arrange
    # handler = MagicMock
    # context = LambdaContext()
    # context.aws_request_id = ""
    # Act
    # setup_logger(None)
    # Assert


def test_import_logger_from_file():
    pass
    # Arrange
    # Act
    # Assert


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
