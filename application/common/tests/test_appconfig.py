from unittest.mock import patch
from ..appconfig import AppConfig
from os import environ

FILE_PATH = "application.common.appconfig"


@patch(f"{FILE_PATH}.AppConfigStore")
def test_app_config(mock_app_config_store):
    # Arrange
    environment = "unittest"
    environ["ENV"] = environment
    feature_flags_name = "event-processor"
    # Act
    AppConfig(feature_flags_name)
    # Assert
    mock_app_config_store.assert_called_once_with(
        environment=environment, application=f"uec-dos-int-{environment}-lambda-app-config", name=feature_flags_name
    )
    # Clean up
    del environ["ENV"]


@patch(f"{FILE_PATH}.FeatureFlags")
@patch(f"{FILE_PATH}.AppConfigStore")
def test_app_config_feature_flags(mock_app_config_store, mock_feature_flags):
    # Arrange
    environment = "unittest"
    environ["ENV"] = environment
    feature_flags_name = "event-processor"
    # Act
    AppConfig(feature_flags_name).get_feature_flags()
    # Assert
    mock_feature_flags.assert_called_once_with(store=mock_app_config_store.return_value)
    # Clean up
    del environ["ENV"]
