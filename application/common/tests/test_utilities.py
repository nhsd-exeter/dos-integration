from os import environ

from pytest import raises

from ..utilities import debug_mode, get_environment_variable


def test_debug_mode_true_local():
    # Arrange
    environ["PROFILE"] = "local"
    # Act
    result = debug_mode()
    # Assert
    assert result is True
    # Clean up
    del environ["PROFILE"]


def test_debug_mode_true_task():
    # Arrange
    environ["PROFILE"] = "task"
    # Act
    result = debug_mode()
    # Assert
    assert result is True
    # Clean up
    del environ["PROFILE"]


def test_debug_mode_false():
    # Arrange
    environ["PROFILE"] = "remote"
    # Act
    result = debug_mode()
    # Assert
    assert result is False
    # Clean up
    del environ["PROFILE"]


def test_get_environment_variable():
    # Arrange
    other_variable_key = "OTHER_VAR"
    other_variable_value = "my-var"
    environ[other_variable_key] = other_variable_value
    # Act
    env_var = get_environment_variable(other_variable_key)
    # Assert
    assert env_var == other_variable_value
    # Clean up
    del environ[other_variable_key]


def test_get_environment_variable_key_error():
    # Act & Assert
    with raises(KeyError):
        get_environment_variable("UNKNOWN_VARIABLE")
