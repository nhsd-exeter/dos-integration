from common.change_event_exceptions import ValidationException
from common.constants import (
    DENTIST_SERVICE_KEY,
    ORGANISATION_SUB_TYPES_KEY,
    ORGANISATION_TYPES_KEY,
    PHARMACY_SERVICE_KEY,
    SERVICE_TYPES,
    VALID_SERVICE_TYPES_KEY,
)


class ServiceType:
    """
    Class for the service type.
    """

    name: str
    organisation_type_id: str
    organisation_sub_type: list[str]
    valid_service_types: set[int]

    def __init__(self, organisation_type_id: str):
        self.name = self.find_service_type(organisation_type_id)
        self.organisation_type_id = SERVICE_TYPES[self.service_type][ORGANISATION_TYPES_KEY]
        self.organisation_type_id = SERVICE_TYPES[self.service_type][ORGANISATION_SUB_TYPES_KEY]
        self.valid_service_types = SERVICE_TYPES[self.service_type][VALID_SERVICE_TYPES_KEY]

    def find_service_type(self, organisation_type_id) -> str:
        if SERVICE_TYPES[PHARMACY_SERVICE_KEY][ORGANISATION_TYPES_KEY] == organisation_type_id:
            service_type = PHARMACY_SERVICE_KEY
        elif SERVICE_TYPES[DENTIST_SERVICE_KEY][ORGANISATION_TYPES_KEY] == organisation_type_id:
            service_type = DENTIST_SERVICE_KEY
        else:
            raise ValidationException(
                f"Unexpected Org Type ID '{organisation_type_id}' not part of {list(SERVICE_TYPES.keys())[0]}"
            )
        return service_type


def set_service_type(service_type_name: str) -> ServiceType:
    """
    Set the service type.
    """
    organisation_type_id = SERVICE_TYPES[service_type_name.upper()][ORGANISATION_TYPES_KEY]
    service_type = ServiceType(organisation_type_id)
    return service_type
