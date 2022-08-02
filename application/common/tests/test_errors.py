from pytest import raises

from ..errors import ValidationException


def test_validation_exception():
    # Arrange & Act
    with raises(ValidationException):
        raise ValidationException("Test")
