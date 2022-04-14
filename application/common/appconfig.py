from os import getenv

from aws_lambda_powertools.utilities.feature_flags.appconfig import AppConfigStore
from aws_lambda_powertools.utilities.feature_flags.feature_flags import FeatureFlags


def get_feature_flags(name: str) -> FeatureFlags:
    """Get the feature flags for the given name

    Args:
        name (str): name of the feature flags configuration profile

    Returns:
        FeatureFlags: feature flags
    """
    environment: str = getenv("ENV")
    app_config = AppConfigStore(
        environment=environment,
        application=f"uec-dos-int-{environment}-lambda-app-config",
        name=name,
    )
    return FeatureFlags(store=app_config)
