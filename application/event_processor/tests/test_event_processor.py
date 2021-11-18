from random import choices
from unittest.mock import MagicMock, patch

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from ..event_processor import EventProcessor, lambda_handler
from ..nhs import NHSEntity
from .conftest import dummy_dos_service

FILE_PATH = "application.event_processor.event_processor"


def test__init__():
    # Arrange
    test_data = {}
    for i in range(10):
        random_str = "".join(choices("ABCDEFGHIJKLM", k=8))
        test_data[random_str] = random_str
    nhs_entity = NHSEntity(test_data)
    # Act
    event_processor = EventProcessor(nhs_entity)
    # Assert
    assert event_processor.nhs_entity == nhs_entity
    assert isinstance(event_processor.matching_services, list)
    assert isinstance(event_processor.change_requests, list)
    assert event_processor.matching_services == []
    assert event_processor.change_requests == []


def test_get_change_requests_full_change_request():
    # Arrange
    service_1 = dummy_dos_service()
    service_1.id = 1
    service_1.uid = 101
    service_1.odscode = "SLC4501"
    service_1.web = "www.fakesite.com"
    service_1.publicphone = "01462622435"
    service_1.postcode = "S45 1AB"

    nhs_entity = NHSEntity({})
    nhs_entity.ODSCode = "SLC45"
    nhs_entity.Website = "www.site.com"
    nhs_entity.Phone = "01462622435"
    nhs_entity.Postcode = "S45 1AA"
    nhs_entity.OrganisationName = "Fake NHS Service"
    nhs_entity.Address1 = "Fake Street1"
    nhs_entity.Address2 = "Fake Street2"
    nhs_entity.Address3 = "Fake Street3"
    nhs_entity.City = "Fake City"
    nhs_entity.County = "Fake County"

    ep = EventProcessor(nhs_entity)
    ep.matching_services = [service_1]
    # Act
    change_requests = ep.get_change_requests()
    # Assert
    assert (
        len(change_requests) == 1
    ), f"Should have 1 change request but more found: {len(change_requests)} change requests"
    cr = change_requests[0]
    for field in ["system", "service_id", "changes"]:
        assert field in cr, f"Field {field} not found in change request"
    assert cr["system"] == "DoS Integration", f"System should be DoS Integration but is {cr['system']}"
    assert cr["changes"] == {
        "website": nhs_entity.Website,
        "postcode": nhs_entity.Postcode,
        "publicname": nhs_entity.OrganisationName,
        "address": [nhs_entity.Address1, nhs_entity.Address2, nhs_entity.Address3, nhs_entity.City, nhs_entity.County],
    }, "Change Request Changes not as expected"


@patch(f"{FILE_PATH}.get_matching_dos_services")
def test_get_matching_services(mock_get_matching_dos_services, change_event):
    # Arrange
    nhs_entity = NHSEntity(change_event)
    service = dummy_dos_service()
    service.typeid = 13
    service.statusid = 1
    mock_get_matching_dos_services.return_value = [service]
    event_processor = EventProcessor(nhs_entity)
    # Act
    matching_services = event_processor.get_matching_services()
    # Assert
    assert matching_services == [service]


@patch(f"{FILE_PATH}.NHSEntity")
@patch(f"{FILE_PATH}.EventProcessor")
def test_lambda_handler(mock_nhs_entity, mock_event_processor, change_event):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    mock_nhs_entity.return_value = MagicMock()
    # Act
    response = lambda_handler(change_event, context)
    # Assert
    assert response is None, f"Response should be None but is {response}"
    mock_nhs_entity.called_once_with(change_event)
    mock_event_processor.called_once_with(mock_nhs_entity.return_value)
