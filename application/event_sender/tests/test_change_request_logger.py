from unittest.mock import patch
from aws_lambda_powertools import Logger
from requests.models import Response
from responses import add as response_add, POST as RESPONSE_POST, activate as responses_activate
from requests import post as request_post
from json import dumps
import pytest

from ..change_request_logger import ChangeRequestLogger


class TestChangeRequestLogger:
    SUCCESS_STATUS_CODES = [200, 201, 202]
    FAILURE_STATUS_CODES = [400, 401, 404, 500]
    CORRELATION_ID = 2

    @patch.object(Logger, "info")
    @pytest.mark.parametrize("status_code", SUCCESS_STATUS_CODES)
    def test_log_change_request_response_success(self, info_logger_mock, status_code: int):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        test_response = Response()
        test_response.status_code = int(status_code)
        test_response._content = b'{"dosChanges": [{"changeId":"2D9B8BB8-F168-1010-E343-7E0FE2822107"}]}'
        expected_extra = {
            "state": "Success",
            "response_status_code": status_code,
            "changes":[{"changeId":"2D9B8BB8-F168-1010-E343-7E0FE2822107"}],
            "response_text": test_response.text,
        }
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
        expected_extra = {
            "state": "Failure",
            "response_status_code": status_code,
            "response_text": test_response.text,
        }
        # Act
        change_request_logger.log_change_request_response(test_response)
        # Assert
        error_logger_mock.assert_called_with("Failed to send change request to DoS", extra=expected_extra)

    @patch.object(Logger, "info")
    @responses_activate
    def test_log_change_request_response(self, info_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        status_code = 201
        changes = [{"changeId":"2D9B8BB8-F168-1010-E343-7E0FE2822107"}]
        response_json = {"dosChanges": changes}
        response_text = dumps(response_json)
        info_logger_expected = {
            "state": "Success",
            "response_status_code": status_code,
            "changes": changes,
            "response_text": response_text,
        }
        response_add(RESPONSE_POST, "https://dummy_url", json=response_json, status=status_code)
        change_request_response = request_post("https://dummy_url", data=response_json)
        # Act
        change_request_logger.log_change_request_response(change_request_response)
        # Assert
        info_logger_mock.assert_called_with("Successfully send change request to DoS", extra=info_logger_expected)

    @patch.object(Logger, "info")
    @patch.object(Logger, "warning")
    @responses_activate
    def test_log_change_request_response_warn_no_changes(self, warn_logger_mock, info_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        status_code = 201
        changes = []
        response_json = {"dosChanges": changes}
        response_text = dumps(response_json)
        info_logger_expected = {
            "state": "Success",
            "response_status_code": status_code,
            "changes": changes,
            "response_text": response_text,
        }
        response_add(RESPONSE_POST, "https://dummy_url", json=response_json, status=status_code)
        change_request_response = request_post("https://dummy_url", data=response_json)
        # Act
        change_request_logger.log_change_request_response(change_request_response)
        # Assert
        info_logger_mock.assert_called_with("Successfully send change request to DoS", extra=info_logger_expected)
        warn_logger_mock.assert_called_with("Change request generated no changes")

    @patch.object(Logger, "info")
    @patch.object(Logger, "warning")
    @responses_activate
    def test_log_change_request_response_warn_none_changes(self, warn_logger_mock, info_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        status_code = 201

        response_json = {"something": ""}
        response_text = dumps(response_json)
        info_logger_expected = {
            "state": "Success",
            "response_status_code": status_code,
            "changes": None,
            "response_text": response_text,
        }
        response_add(RESPONSE_POST, "https://dummy_url", json=response_json, status=status_code)
        change_request_response = request_post("https://dummy_url", data=response_json)
        # Act
        change_request_logger.log_change_request_response(change_request_response)
        # Assert
        info_logger_mock.assert_called_with("Successfully send change request to DoS", extra=info_logger_expected)
        warn_logger_mock.assert_called_with("Change request generated no changes")


    @patch.object(Logger, "exception")
    def test_log_change_request_exception(self, exception_logger_mock):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        expected_extra = {
            "state": "Exception",
            "exception_reason": "Error posting change request",
        }
        # Act
        change_request_logger.log_change_request_exception()
        # Assert
        exception_logger_mock.assert_called_with("Exception error posting change request to DoS", extra=expected_extra)
