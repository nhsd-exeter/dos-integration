import random

import pytest

from dos import *


def test__init__():
    """Pass in random list of values as a mock database row then make sure
    they're correctly set as the attributes of the created object.
    """

    # Create random fake data
    test_db_row = []
    for column in DoSService.db_columns:
        random_str = "".join(random.choices("ABCDEFGHIJKLM", k=8))
        test_db_row.append(random_str)
    test_db_row = tuple(test_db_row)

    # Create object
    dos_service = DoSService(test_db_row)

    # Check object
    for i, column in enumerate(DoSService.db_columns):
        assert getattr(dos_service, column) == test_db_row[i]


def test_ods5():

    # Create random fake data
    test_db_row = []
    for column in DoSService.db_columns:
        random_str = "".join(random.choices("ABCDEFGHIJKLM", k=8))
        test_db_row.append(random_str)

    # Insert specfic ODScode
    ods_index = DoSService.db_columns.index("odscode")
    test_db_row[ods_index] = "SLC92823732"

    # Create object
    dos_service = DoSService(test_db_row)

    assert dos_service.ods5() == "SLC92"


def test_get_changes():

    # Create random fake data
    test_db_row = []
    for column in DoSService.db_columns:
        random_str = "".join(random.choices("ABCDEFGHIJKLM", k=8))
        test_db_row.append(random_str)
    test_db_row = tuple(test_db_row)

    # Create DoSService object with fake data
    dos_service = DoSService(test_db_row)

    # Create NHSEntity with same data
    nhs_kwargs = {"website": dos_service.web}
    nhs_entity = NHSEntity(nhs_kwargs)

    # Changes should be empty when checked
    assert dos_service.get_changes(nhs_entity) == {}

    # Create NHSEntity with different web field but rest the same
    nhs_kwargs = {"website": "changed-website.com", "publicphone": dos_service.publicphone}
    nhs_entity = NHSEntity(nhs_kwargs)

    expected_changes = {"website": "changed-website.com"}
    assert dos_service.get_changes(nhs_entity) == expected_changes


def test_get_matching_dos_services():

    # odscode too short should raise exception
    with pytest.raises(Exception):
        get_matching_dos_services("FA00")

    # Test with non-matching odscode, should return nothing
    assert get_matching_dos_services("@1234") == []
