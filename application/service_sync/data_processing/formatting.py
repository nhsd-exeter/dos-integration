from re import sub
from urllib.parse import urlparse, urlunparse

from aws_lambda_powertools import Logger

logger = Logger()


def format_address(address: str) -> str:
    """Formats an address line to title case and removes apostrophes. As well it replaces any '&' symbols with and.

    Args:
        address (str): Address line to format

    Returns:
        str: Formatted address line
    """
    # Capitalise first letter of each word
    formatted_address = sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), address)
    formatted_address = formatted_address.replace("'", "")  # Remove apostrophes
    formatted_address = formatted_address.replace("&", "and")  # Replace '&' with 'and'
    logger.debug("Formatted address line", prior_address=address, formatted_address=formatted_address)
    return formatted_address


def format_website(website: str) -> str:
    """Formats a website to lowercase and removes trailing slash.

    Args:
        website (str): Website to format

    Returns:
        str: Formatted website
    """
    nhs_uk_website = urlparse(website)
    if nhs_uk_website.netloc:  # handle websites like https://www.test.com
        nhs_uk_website = nhs_uk_website._replace(netloc=nhs_uk_website.netloc.lower())
        nhs_uk_website = urlunparse(nhs_uk_website)
    elif "/" in website:
        nhs_uk_website = website.split("/")
        nhs_uk_website[0] = nhs_uk_website[0].lower()
        nhs_uk_website = "/".join(nhs_uk_website)
    else:  # handle website like www.test.com
        nhs_uk_website = urlunparse(nhs_uk_website).lower()
    logger.debug("Formatted website", prior_website=website, formatted_website=nhs_uk_website)
    return nhs_uk_website


def format_public_phone(phone: str) -> str:
    """Formats a phone number to remove spaces.

    Args:
        phone (str): Phone number to format

    Returns:
        str: Formatted phone number
    """
    formatted_phone = phone.strip()
    formatted_phone = formatted_phone.replace(" ", "")
    logger.debug("Formatted phone", prior_phone=phone, formatted_phone=formatted_phone)
    return formatted_phone
