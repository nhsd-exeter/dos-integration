import random

import pytest

from event_processor import *
from nhs import NHSEntity
from dos import DoSService, dummy_dos_service


def test__init__():

    # Create dict of fake random data
    test_data = {}
    for i in range(10):
        random_str = "".join(random.choices("ABCDEFGHIJKLM", k=8))
        test_data[random_str] = random_str

    # Create test objects
    nhs_entity = NHSEntity(test_data)
    ep = EventProcessor(nhs_entity)

    # Assert initial values are as expected
    assert ep.nhs_entity == nhs_entity
    assert ep.matching_services is None
    assert ep.change_requests is None


def test_get_change_requests():
    trace_id = environ.get("_X_AMZN_TRACE_ID", default="<NO-TRACE-ID>")

    # Create test services and nhs entity
    service_1 = dummy_dos_service()
    service_1.id = 1
    service_1.uid = 101
    service_1.odscode = "SLC4501"
    service_1.web = "www.fakesite.com"
    service_1.publicphone = "01462622435"

    service_2 = dummy_dos_service()
    service_2.id = 2
    service_2.uid = 102
    service_2.odscode = "SLC4502"
    service_2.web = "www.fakesite.com"
    service_2.publicphone = "01462622435"

    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.fakesite.com"
    nhs_entity.publicphone = "01462622435"

    # Create test processor and input our services
    # as matching services
    ep = EventProcessor(nhs_entity)
    ep.matching_services = [service_1, service_2]

    # Expect 0 change requests from original data
    change_requests = ep.get_change_requests()
    assert change_requests == []

    # Change website in service 1 and get changes again
    service_1.web = "differentwebsite.com"
    change_requests = ep.get_change_requests()

    # validate change request 
    assert len(change_requests) == 1
    cr = change_requests[0]
    for field in ["system", "service_id", "changes"]:
        assert field in cr
    assert cr["system"] == "DoS Integration"
    assert cr["changes"] == {"website": nhs_entity.website}


    # Change website in service 2 and get changes again
    service_2.web = "differentwebsite2.com"
    change_requests = ep.get_change_requests()

    # validate each change request
    assert len(change_requests) == 2
    for cr in change_requests:
        for field in ["system", "service_id", "changes"]:
            assert field in cr
        assert cr["system"] == "DoS Integration"
        assert cr["changes"] == {"website": nhs_entity.website}



def test_get_matching_services():
    # Create entity
    nhs_entity = NHSEntity({})
    nhs_entity.odscode = "SLC45"
    nhs_entity.website = "www.fakesite.com"
    nhs_entity.publicphone = "01462622435"

    # Create test processor and input our services
    # as matching services
    ep = EventProcessor(nhs_entity)



def test_lamda_handler():

    # Fake test input should yield no results in db
    dummy_entity_data = {
        "odscode": "F@T67",
        "website": "www.pharmacywebsite.com",
        "publicname": "Cool Pharmacy 4 U",
        "phone": "441462622788",
        }

    # Create test payload for lambda
    event = {
        "entity": dummy_entity_data,
        "send_changes": False
        }

    # Run lambda and check ouput
    result = lambda_handler(event, None)

    assert isinstance(result, dict)
    assert "statusCode" in result

    # Remove env var and check failure
    del environ["DB_SERVER"]
    result = lambda_handler(event, None)
    assert result["statusCode"] == 400
    assert "error" in result
