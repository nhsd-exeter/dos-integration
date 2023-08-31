from json import loads
from time import sleep, time

from requests import get

from .aws.secrets_manager import get_secret


def slack_retry(message: str) -> str:
    """Retries slack message for 5 minutes.

    Args:
        message (str): Message to check for

    Raises:
        ValueError: If message is not found in slack

    Returns:
        str: Response from slack
    """
    slack_channel, slack_oauth = slack_secrets()
    for _ in range(6):
        sleep(60)
        response_value = check_slack(slack_channel, slack_oauth)
        if message in response_value:
            return response_value
    msg = f"Slack alert message not found, message: {message}"
    raise ValueError(msg)


def slack_secrets() -> tuple[str, str]:
    """Gets the slack secrets from AWS secrets manager.

    Returns:
        tuple[str, str]: Slack channel and slack oauth token
    """
    slack_secrets = loads(get_secret("uec-dos-int-dev/deployment"))
    return slack_secrets["SLACK_CHANNEL"], slack_secrets["SLACK_OAUTH"]


def check_slack(channel: str, token: str) -> str:
    """Gets slack messages for the specified channel.

    Args:
        channel (str): Slack channel to get messages for
        token (str): Slack token to use for authentication

    Returns:
        str: Response text from the slack API
    """
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    current = str(time() - 3600)
    output = get(
        url=f"https://slack.com/api/conversations.history?channel={channel}&oldest={current}",
        headers=headers,
        timeout=10,
    )
    return output.text
