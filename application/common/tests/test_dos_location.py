import pytest

from application.common.dos_location import DoSLocation
from application.conftest import dummy_dos_location


@pytest.mark.parametrize(
    ("dos_location", "expected_result"),
    [
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=None,
                northing=None,
                postaltown="TOWN",
                latitude=None,
                longitude=None,
            ),
            False,
        ),
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=None,
                northing=1,
                postaltown="TOWN",
                latitude=1.1,
                longitude=1.1,
            ),
            False,
        ),
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=1,
                northing=None,
                postaltown="TOWN",
                latitude=1.1,
                longitude=1.1,
            ),
            False,
        ),
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=1,
                northing=1,
                postaltown="TOWN",
                latitude=None,
                longitude=1.1,
            ),
            False,
        ),
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=1,
                northing=1,
                postaltown="TOWN",
                latitude=1.1,
                longitude=None,
            ),
            False,
        ),
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=None,
                northing=None,
                postaltown="TOWN",
                latitude=1.1,
                longitude=1.1,
            ),
            False,
        ),
        (
            DoSLocation(
                id=1,
                postcode="TE57ER",
                easting=1,
                northing=1,
                postaltown="TOWN",
                latitude=None,
                longitude=None,
            ),
            False,
        ),
        (
            DoSLocation(id=1, postcode="TE57ER", easting=1, northing=1, postaltown="TOWN", latitude=1.1, longitude=1.1),
            True,
        ),
    ],
)
def test_doslocation_is_valid(dos_location: DoSLocation, expected_result: bool) -> None:
    actual_result = dos_location.is_valid()
    assert (
        actual_result is expected_result
    ), f"is_valued check on {dos_location} was found to be {actual_result}, it should be {expected_result}."


@pytest.mark.parametrize(
    ("input_postcode", "expected_result"),
    [
        ("TE57ER", "TE57ER"),
        ("TE5 7ER", "TE57ER"),
        ("T E57ER", "TE57ER"),
        ("T E57E R", "TE57ER"),
        ("T E 5 7 E R", "TE57ER"),
        ("TE57ER  ", "TE57ER"),
        ("   TE57ER", "TE57ER"),
        ("te5 7er", "TE57ER"),
        ("te5  7 e   r", "TE57ER"),
    ],
)
def test_doslocation_normal_postcode(input_postcode: str, expected_result: str) -> None:
    dos_location = dummy_dos_location()
    dos_location.postcode = input_postcode
    actual_output = dos_location.normal_postcode()
    assert (
        actual_output == expected_result
    ), f"Normalised postcode for '{input_postcode}' is '{actual_output}', it should be '{expected_result}'."
