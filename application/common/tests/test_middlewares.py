import logging
from pytest import raises

from botocore.exceptions import ClientError

from application.common.middlewares import unhandled_exception_logging


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
        assert "dummy exception message" in caplog.text
