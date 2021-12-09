from http.client import HTTPConnection
from os import environ
from unittest.mock import patch
from aws_lambda_powertools import Logger
import pytest
from requests.models import Response

from ..change_request_logger import ChangeRequestLogger


class TestChangeRequestLogger:
    SUCCESS_STATUS_CODES = [200, 201, 202]
    FAILURE_STATUS_CODES = [400, 401, 404, 500]

    @patch.object(Logger, "info")
    @pytest.mark.parametrize("status_code", SUCCESS_STATUS_CODES)
    def test_log_change_request_response_success(self, info_logger_mock, status_code: int):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        test_response = Response()
        test_response.status_code = int(status_code)
        test_response._content = b'{ "key" : "a" }'
        expected_extra = {"state": "Success", "response_status_code": status_code, "response_text": test_response.text}
        # Act
        change_request_logger.log_change_request_response(test_response)
        # Assert
        info_logger_mock.assert_called_with("Successfully send change request to DoS", extra=expected_extra)

    @patch.object(Logger, "error")
    @pytest.mark.parametrize("status_code", FAILURE_STATUS_CODES)
    def test_log_change_request_response_failure(self, error_logger_mock, status_code: int):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        test_response = Response()
        test_response.status_code = int(status_code)
        test_response._content = b'{ "key" : "a" }'
        expected_extra = {"state": "Failure", "response_status_code": status_code, "response_text": test_response.text}
        # Act
        change_request_logger.log_change_request_response(test_response)
        # Assert
        error_logger_mock.assert_called_with("Failed to send change request to DoS", extra=expected_extra)

    @patch.object(Logger, "info")
    def test_log_change_request_body_development(self, info_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        change_request_body = '{"my-key": "my-var"}'
        environ["PROFILE"] = "task"
        # Act
        change_request_logger.log_change_request_body(change_request_body)
        # Assert
        info_logger_mock.assert_called_with(
            "Change Request to DoS payload", extra={"change_request_body": change_request_body}
        )
        assert HTTPConnection.debuglevel == 1
        # Clean up
        HTTPConnection.debuglevel = 0
        del environ["PROFILE"]

    @patch.object(Logger, "info")
    def test_log_change_request_body_production(self, info_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        change_request_body = '{"my-key": "my-var"}'
        environ["PROFILE"] = "dev"
        # Act
        change_request_logger.log_change_request_body(change_request_body)
        # Assert
        info_logger_mock.assert_called_with(
            "Change Request to DoS payload", extra={"change_request_body": change_request_body}
        )
        assert HTTPConnection.debuglevel == 0
        # Clean up
        del environ["PROFILE"]

    @patch.object(Logger, "exception")
    def test_log_change_request_exception(self, exception_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        expected_extra = {"state": "Exception", "exception_reason": "Error posting change request"}
        # Act
        change_request_logger.log_change_request_exception()
        # Assert
        exception_logger_mock.assert_called_with("Exception error posting change request to DoS", extra=expected_extra)
