from os import getenv
from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.feature_flags.appconfig import AppConfigStore
from aws_lambda_powertools.utilities.feature_flags.feature_flags import FeatureFlags

logger = Logger(child=True)


class AppConfig:
    """Application configuration"""

    def __init__(self, name: str) -> None:
        """Initialise the application configuration

        Args:
            name (str): name of the application configuration profile
        """
        logger.debug("Setting up AppConfigStore")
        self.name = name
        environment: str = getenv("ENV")
        self.app_config = AppConfigStore(
            environment=environment,
            application=f"uec-dos-int-{environment}-lambda-app-config",
            name=name,
        )
        logger.debug(f"AppConfigStore setup complete: {self.app_config}")

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
        logger.debug("Getting feature flags from AppConfigStore")
        feature_flags = FeatureFlags(store=self.app_config)
        logger.debug(f"Retreived feature flags {feature_flags}")
        return feature_flags
