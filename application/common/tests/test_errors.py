import pytest

from application.common.errors import DynamoDBError, ValidationError


def test_validation_exception() -> None:
    # Arrange & Act
    with pytest.raises(ValidationError):  # noqa: PT012
        msg = "Test"
        raise ValidationError(msg)


def test_dynamodb_exception() -> None:
    # Arrange & Act
    with pytest.raises(DynamoDBError):  # noqa: PT012
        msg = "Test"
        raise DynamoDBError(msg)
