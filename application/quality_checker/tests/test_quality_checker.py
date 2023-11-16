from dataclasses import dataclass
from unittest.mock import MagicMock, call, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext

from application.quality_checker.quality_checker import (
    check_dos_data_quality,
    lambda_handler,
)
from common.commissioned_service_type import BLOOD_PRESSURE, CONTRACEPTION

FILE_PATH = "application.quality_checker.quality_checker"


@pytest.fixture()
def lambda_context() -> None:
    @dataclass
    class LambdaContext:
        """Mock LambdaContext - All dummy values."""

        function_name: str = "quality-checker"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = "arn:aws:lambda:eu-west-1:000000000:function:quality-checker"
        aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"

    return LambdaContext()


@patch(f"{FILE_PATH}.check_dos_data_quality")
def test_lambda_handler(
    mock_check_dos_data_quality: MagicMock,
    lambda_context: LambdaContext,
) -> None:
    # Arrange
    event = {}
    # Act
    lambda_handler(event, lambda_context)
    # Assert
    mock_check_dos_data_quality.assert_called_once_with()


@patch(f"{FILE_PATH}.check_for_zcode_profiling_on_incorrect_type")
@patch(f"{FILE_PATH}.check_pharmacy_profiling")
@patch(f"{FILE_PATH}.connect_to_db_reader")
def test_check_dos_data_quality(
    mock_connect_to_db_reader: MagicMock,
    mock_check_pharmacy_profiling: MagicMock,
    mock_check_for_zcode_profiling_on_incorrect_type: MagicMock,
) -> None:
    # Arrange
    # Act
    check_dos_data_quality()
    # Assert
    mock_connect_to_db_reader.assert_called_once_with()
    mock_check_pharmacy_profiling.assert_called_once_with(
        mock_connect_to_db_reader().__enter__(),
    )
    mock_check_for_zcode_profiling_on_incorrect_type.assert_has_calls(
        calls=[
            call(mock_connect_to_db_reader().__enter__(), BLOOD_PRESSURE),
            call(mock_connect_to_db_reader().__enter__(), CONTRACEPTION),
        ],
    )
