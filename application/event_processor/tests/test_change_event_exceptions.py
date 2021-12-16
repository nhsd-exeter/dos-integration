from pytest import raises

from ..change_event_exceptions import ValidationException


def test_validation_exception():
    # Arrange & Act
    with raises(ValidationException):
        raise ValidationException("Test")
