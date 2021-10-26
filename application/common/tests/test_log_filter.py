from logging import LogRecord
from os import environ

from aws_lambda_context import LambdaContext

from ..log_filter import LogFilter


class TestLogFilter:
    def test__init__(self):
        # Arrange
        request_id = "request_id"
        function_name = "function_name"
        small_trace_id = "0000-00000-00000"
        x_ray_trace_id_full = f"Root={small_trace_id};Parent=20b1cb9a018a0990;Sampled=1"
        environ["_X_AMZN_TRACE_ID"] = x_ray_trace_id_full
        environ["AWS_LAMBDA_FUNCTION_NAME"] = function_name
        lambda_context = LambdaContext()
        lambda_context.function_name = function_name
        lambda_context.aws_request_id = request_id
        # Act
        log_filter = LogFilter(lambda_context)
        # Assert
        assert log_filter.aws_request_id == request_id
        assert log_filter.function_name == function_name
        assert log_filter.x_ray_trace_id == small_trace_id
        # Clean up
        del environ["_X_AMZN_TRACE_ID"]
        del environ["AWS_LAMBDA_FUNCTION_NAME"]

    def test__init__no_x_ray_trace_id(self):
        # Arrange
        request_id = "request_id"
        function_name = "function_name"
        environ["AWS_LAMBDA_FUNCTION_NAME"] = function_name
        lambda_context = LambdaContext()
        lambda_context.function_name = function_name
        lambda_context.aws_request_id = request_id
        # Act
        log_filter = LogFilter(lambda_context)
        # Assert
        assert log_filter.aws_request_id == "request_id"
        assert log_filter.function_name == function_name
        assert log_filter.x_ray_trace_id == "NA"
        # Clean up
        del environ["AWS_LAMBDA_FUNCTION_NAME"]

    def test_filter(self):
        # Arrange
        request_id = "request_id"
        function_name = "function_name"
        environ["AWS_LAMBDA_FUNCTION_NAME"] = function_name
        lambda_context = LambdaContext()
        lambda_context.function_name = function_name
        lambda_context.aws_request_id = request_id
        log_filter = LogFilter(lambda_context)
        log_record = LogRecord(
            name="lambda",
            level=20,
            pathname="/var/task/event_sender.py",
            lineno=21,
            msg="Test",
            exc_info=None,
            args=None,
        )
        # Act
        response = log_filter.filter(log_record)
        # Assert
        assert response is True
        # Clean up
        del environ["AWS_LAMBDA_FUNCTION_NAME"]
