from typing import Union

from aws_lambda_powertools import Logger
from common.change_event_exceptions import ValidationException
from common.constants import ORGANISATION_SUB_TYPES_KEY, SERVICE_TYPES, SERVICE_TYPES_NAME_KEY, VALID_SERVICE_TYPES_KEY

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
        if SERVICE_TYPES.get(organisation_type_id) is None:
            raise ValidationException(
                f"Unexpected Org Type ID '{organisation_type_id}' not part of {list(SERVICE_TYPES.keys())[0]}"
            )
        self.name = SERVICE_TYPES[organisation_type_id][SERVICE_TYPES_NAME_KEY]
        self.organisation_type_id = organisation_type_id
        self.organisation_sub_type = SERVICE_TYPES[organisation_type_id][ORGANISATION_SUB_TYPES_KEY]
        self.valid_service_types = SERVICE_TYPES[organisation_type_id][VALID_SERVICE_TYPES_KEY]
        logger.debug(f"ServiceType: {self.name}")

    def __repr__(self) -> str:
        return f"<ServiceType: name={self.name} valid_service_types={self.valid_service_types}>"


def get_valid_service_types(organisation_type_id: str) -> set[int]:
    """Get the valid service types for the organisation type id

    Args:
        organisation_type_id (str): organisation type id from nhs uk entity

    Returns:
        set[int]: set of valid service types
    """
    return SERVICE_TYPES[organisation_type_id][VALID_SERVICE_TYPES_KEY]


def get_service_type(service_type_name: str) -> Union[ServiceType, None]:
    """get the service type based on the service type name

    Args:
        service_type_name (str): service type name

    Returns:
        Union[ServiceType, None]: service type object or None
    """
    for key in SERVICE_TYPES.keys():
        if SERVICE_TYPES[key][SERVICE_TYPES_NAME_KEY] == service_type_name.upper():
            return ServiceType(key)
