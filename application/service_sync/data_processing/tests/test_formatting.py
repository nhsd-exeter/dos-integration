import pytest

from application.service_sync.data_processing.formatting import format_address, format_public_phone, format_website


@pytest.mark.parametrize(
    ("address", "formatted_address"),
    [
        ("3rd Floor", "3Rd Floor"),
        ("24 Hour Road", "24 Hour Road"),
        ("Green Tye", "Green Tye"),
        ("Much Hadham", "Much Hadham"),
        ("Herts", "Herts"),
        ("24 hour road", "24 Hour Road"),
        ("green tye & woodsham", "Green Tye and Woodsham"),
        ("much hadham", "Much Hadham"),
        ("county", "County"),
        ("32A unit", "32A Unit"),
        ("george's road", "Georges Road"),
        ("green tye", "Green Tye"),
        ("less hadham", "Less Hadham"),
        ("testerset", "Testerset"),
        ("ABCDE", "Abcde"),
        ("WOODCHURCH ROAD", "Woodchurch Road"),
        ("TESTERSHIRE", "Testershire"),
    ],
)
def test_format_address(address: str, formatted_address: str) -> None:
    assert formatted_address == format_address(address)


@pytest.mark.parametrize(
    ("website", "formatted_website"),
    [
        ("www.test.com", "www.test.com"),
        ("www.Test.com", "www.test.com"),
        ("www.test.com/", "www.test.com/"),
        ("www.TEST.Com", "www.test.com"),
        ("www.Test.com/TEST", "www.test.com/TEST"),
        ("www.rowlandspharmacy.co.uk/test?foo=test", "www.rowlandspharmacy.co.uk/test?foo=test"),
        ("https://www.Test.com", "https://www.test.com"),
        ("https://www.test.com/", "https://www.test.com/"),
        ("https://www.TEST.Com", "https://www.test.com"),
        ("https://www.Test.com/TEST", "https://www.test.com/TEST"),
        ("https://www.rowlandspharmacy.co.uk/test?foo=test", "https://www.rowlandspharmacy.co.uk/test?foo=test"),
    ],
)
def test_format_website(website: str, formatted_website: str) -> None:
    assert formatted_website == format_website(website)


@pytest.mark.parametrize(
    ("phone", "formatted_phone"),
    [
        (" 0123456789", "0123456789"),
        ("01234 56789", "0123456789"),
        ("01234 56789 ", "0123456789"),
        ("01 234 5678 9", "0123456789"),
        ("01234  56789  ", "0123456789"),
    ],
)
def test_format_public_phone(phone: str, formatted_phone: str) -> None:
    assert formatted_phone == format_public_phone(phone)
