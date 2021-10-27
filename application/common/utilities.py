from os import environ
from logging import getLogger


def debug_mode() -> bool:
    """This function checks if debug mode should be enabled

    Returns:
        bool: Should debug mode be on?
    """
    response = False
    if environ["PROFILE"] in ["local", "task"]:
        response = True
    return response


def get_environment_variable(environment_key: str) -> str:
    """[summary]

    Args:
        environment_key (str): [description]

    Raises:
        KeyError: If environment variable not set

    Returns:
        str: [description]
    """
    try:
        return environ[environment_key]
    except KeyError as e:
        logger = getLogger("lambda")
        logger.exception(f"Environment variable not found {environment_key}")
        raise e
