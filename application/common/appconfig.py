from os import getenv
from typing import Any, Dict

from aws_lambda_powertools.utilities.feature_flags.appconfig import AppConfigStore
from aws_lambda_powertools.utilities.feature_flags.feature_flags import FeatureFlags


class AppConfig:
    """Application configuration"""

    def __init__(self, name: str) -> None:
        """Initialise the application configuration

        Args:
            name (str): name of the application configuration profile
        """
        self.name = name
        environment: str = getenv("ENV")
        self.app_config = AppConfigStore(
            environment=environment,
            application=f"uec-dos-int-{environment}-lambda-app-config",
            name=name,
        )

    def get_raw_configuration(self) -> Dict[str, Any]:
        """Get the raw configuration

        Returns:
            dict: raw configuration
        """
        return self.app_config.get_raw_configuration

    def get_feature_flags(self) -> FeatureFlags:
        """Get the feature flags for the given name

        Returns:
            FeatureFlags: feature flags class
        """
        return FeatureFlags(store=self.app_config)
