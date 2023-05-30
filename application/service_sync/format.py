from re import sub
from urllib.parse import urlparse, urlunparse


def format_address(address: str) -> str:
    """Formats an address line to title case and removes apostrophes. As well it replaces any '&' symbols with and.

    Args:
        address (str): Address line to format

    Returns:
        str: Formatted address line
    """
    address = sub(
        r"[A-Za-z]+('[A-Za-z]+)?",
        lambda word: word.group(0).capitalize(),
        address,
    )  # Capitalise first letter of each word
    address = address.replace("'", "")  # Remove apostrophes
    address = address.replace("&", "and")  # Replace '&' with 'and'
    return address


def format_website(website: str) -> str:
    """Formats a website to lowercase and removes trailing slash.

    Args:
        website (str): Website to format

    Returns:
        str: Formatted website
    """
    nhs_uk_website = urlparse(website)
    if nhs_uk_website.netloc:  # handle website like https://www.test.com
        nhs_uk_website = nhs_uk_website._replace(netloc=nhs_uk_website.netloc.lower())
        nhs_uk_website = urlunparse(nhs_uk_website)
    elif "/" in website:
        nhs_uk_website = website.split("/")
        nhs_uk_website[0] = nhs_uk_website[0].lower()
        nhs_uk_website = "/".join(nhs_uk_website)
    else:
        nhs_uk_website = urlunparse(nhs_uk_website).lower()
    return nhs_uk_website
