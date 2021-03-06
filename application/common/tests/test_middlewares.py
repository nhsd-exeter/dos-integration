import logging

from aws_lambda_powertools.utilities.data_classes import SQSEvent
from botocore.exceptions import ClientError
from pytest import raises

from ..middlewares import set_correlation_id, unhandled_exception_logging


def test_unhandled_exception_logging(caplog):
    @unhandled_exception_logging
    def client_error_func(event, context):
        raise ClientError({"Error": {"Code": "dummy_error", "Message": "dummy_message"}}, "op_name")

    @unhandled_exception_logging
    def regular_error_func(event, context):
        raise Exception("dummy exception message")

    with caplog.at_level(logging.ERROR):

        with raises(ClientError):
            client_error_func(None, None)
        assert "Boto3 Client Error - 'dummy_error': dummy_message" in caplog.text

        with raises(Exception):
            regular_error_func(None, None)
        assert "dummy_error" in caplog.text


def test_unhandled_exception_logging_no_error():
    @unhandled_exception_logging
    def dummy_handler(event, context):
        pass

    # Arrange
    event = SQSEvent(None)
    # Act
    dummy_handler(event, None)


def test_set_correlation_id(caplog, lambda_context, dead_letter_message):
    @set_correlation_id()
    def dummy_handler(event, context):
        pass

    # Arrange
    event = SQSEvent(dead_letter_message)
    # Act
    dummy_handler(event, lambda_context)
