from json import loads
from os import getenv

from .aws import get_secret


def get_api_key() -> str:
    """Get the api key from AWS secrets manager."""
    api_key_json = get_secret(getenv("API_KEY_SECRET"))
    return loads(api_key_json)[getenv("NHS_UK_API_KEY")]
