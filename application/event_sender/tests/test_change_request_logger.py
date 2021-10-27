from http.client import HTTPConnection
from os import environ

import pytest
from pytest import fixture
from requests.models import Response
from testfixtures import LogCapture

from ..change_request_logger import ChangeRequestLogger
from logging import getLogger


class TestChangeRequestLogger:
    SUCCESS_STATUS_CODES = [200, 201, 202]
    FAILURE_STATUS_CODES = [400, 401, 404, 500]

    def test__init__(self):
        # Arrange
        # Act
        change_request_logger = ChangeRequestLogger()
        # Assert
        assert change_request_logger.logger == getLogger("lambda")

    @pytest.mark.parametrize("status_code", SUCCESS_STATUS_CODES)
    def test_log_change_request_response_success(self, status_code: int, log_capture):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        test_response = Response()
        test_response.status_code = int(status_code)
        test_response._content = b'{ "key" : "a" }'
        # Act
        change_request_logger.log_change_request_response(test_response)
        # Assert
        log_capture.check(
            ("lambda", "INFO", f"CHANGE_REQUEST|Success|{status_code}|{{'key': 'a'}}"),
        )

    @pytest.mark.parametrize("status_code", FAILURE_STATUS_CODES)
    def test_log_change_request_response_failure(self, status_code: int, log_capture):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        test_response = Response()
        test_response.status_code = int(status_code)
        test_response._content = b'{ "key" : "a" }'
        # Act
        change_request_logger.log_change_request_response(test_response)
        # Assert
        log_capture.check(
            ("lambda", "ERROR", f"CHANGE_REQUEST|Failure|{status_code}|{{'key': 'a'}}"),
        )

    def test_log_change_request_body_development(self, log_capture):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        change_request_body = '{"my-key": "my-var"}'
        environ["PROFILE"] = "task"
        # Act
        change_request_logger.log_change_request_body(change_request_body)
        # Assert
        log_capture.check(
            ("lambda", "INFO", f"CHANGE_REQUEST|{change_request_body=}"),
        )
        assert HTTPConnection.debuglevel == 1
        # Clean up
        HTTPConnection.debuglevel = 0
        del environ["PROFILE"]

    def test_log_change_request_body_production(self, log_capture):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        change_request_body = '{"my-key": "my-var"}'
        environ["PROFILE"] = "dev"
        # Act
        change_request_logger.log_change_request_body(change_request_body)
        # Assert
        log_capture.check(
            ("lambda", "INFO", f"CHANGE_REQUEST|{change_request_body=}"),
        )
        assert HTTPConnection.debuglevel == 0
        # Clean up
        del environ["PROFILE"]


@fixture()
def log_capture():
    with LogCapture(names="lambda") as capture:
        yield capture
