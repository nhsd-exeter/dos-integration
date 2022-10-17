from pytest import raises

from ..errors import DynamoDBException, ValidationException


def test_validation_exception():
    # Arrange & Act
    with raises(ValidationException):
        raise ValidationException("Test")


def test_dynamodb_exception():
    # Arrange & Act
    with raises(DynamoDBException):
        raise DynamoDBException("Test")
