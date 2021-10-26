from requests.models import Response
import pytest
from ..change_request_logger import ChangeRequestLogger


class TestChangeRequestLogger:
    SUCCESS_STATUS_CODES = [200, 201, 202]
    FAILURE_STATUS_CODES = [400, 401, 404]

    def test__init__(self):
        pass

    @pytest.mark.parametrize("status_code", SUCCESS_STATUS_CODES)
    def test_log_change_request_response_success(self, status_code: int):
        # Arrange
        change_request_logger = ChangeRequestLogger()
        test_response = Response()
        test_response.status_code = int(status_code)
        # Act
        change_request_logger.log_change_request_response(test_response)
        # Assert

    @pytest.mark.parametrize("status_code", FAILURE_STATUS_CODES)
    def test_log_change_request_response_failure(self, status_code: int):
        pass

    def log_change_request_body_development(self):
        pass

    def log_change_request_body_production(self):
        pass
