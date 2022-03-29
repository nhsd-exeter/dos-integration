from aws_lambda_powertools import Logger
from common.change_event_exceptions import ValidationException
from common.constants import (
    DENTIST_SERVICE_KEY,
    ORGANISATION_SUB_TYPES_KEY,
    ORGANISATION_TYPES_KEY,
    PHARMACY_SERVICE_KEY,
    SERVICE_TYPES,
    VALID_SERVICE_TYPES_KEY,
)

logger = Logger(child=True)


class ServiceType:
    """
    Class for the service type.
    """

    name: str
    organisation_type_id: str
    organisation_sub_type: list[str]
    valid_service_types: set[int]

    def __init__(self, organisation_type_id: str):
        self.name = self._find_service_type_name(organisation_type_id)
        self.organisation_type_id = SERVICE_TYPES[self.name][ORGANISATION_TYPES_KEY]
        self.organisation_sub_type = SERVICE_TYPES[self.name][ORGANISATION_SUB_TYPES_KEY]
        self.valid_service_types = SERVICE_TYPES[self.name][VALID_SERVICE_TYPES_KEY]
        logger.debug(f"ServiceType: {self.name}")

    def __repr__(self) -> str:
        return f"<ServiceType: name={self.name} valid_service_types={self.valid_service_types}>"

    def _find_service_type_name(self, organisation_type_id: str) -> str:
        """Select the service type name based on the organisation type id.
        This is an internal method not intended for changing service type.

        Args:
            organisation_type_id (str): organisation type id of NHS entity

        Raises:
            ValidationException: if the organisation type id is not found in the valid service types

        Returns:
            str: service type name
        """
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
    """Set the service type based on the service type name

    Args:
        service_type_name (str): service type name

    Returns:
        ServiceType: service type object
    """
    organisation_type_id = SERVICE_TYPES[service_type_name.upper()][ORGANISATION_TYPES_KEY]
    service_type = ServiceType(organisation_type_id)
    return service_type
