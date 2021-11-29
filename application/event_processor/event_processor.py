from json import dumps
from logging import getLogger
from os import environ, getenv
import sys
sys.path.append("../")

from aws_lambda_powertools import Tracer
from boto3 import client

from common.logger import setup_logger
from common.utilities import is_mock_mode, invoke_lambda_function
from opening_times import export_cr_format_spec_list
from change_request import (
    ChangeRequest,
    ADDRESS_CHANGE_KEY,
    PHONE_CHANGE_KEY,
    POSTCODE_CHANGE_KEY,
    PUBLICNAME_CHANGE_KEY,
    WEBSITE_CHANGE_KEY,
    OPENING_DATES_KEY,
    OPENING_DAYS_KEY
)
from dos import (
    VALID_SERVICE_TYPES, 
    VALID_STATUS_ID, 
    DoSService, 
    get_matching_dos_services
)
from nhs import NHSEntity

logger = getLogger("lambda")
tracer = Tracer()
lambda_client = client("lambda", region_name=getenv("AWS_REGION", default="eu-west-2"))
expected_env_vars = ("DB_SERVER", "DB_PORT", "DB_NAME", "DB_USER_NAME", "EVENT_SENDER_LAMBDA_NAME")


class EventProcessor:

    def __init__(self, nhs_entity):
        self.nhs_entity = nhs_entity
        self.matching_services = None
        self.change_requests = None

    def get_matching_services(self):
        """Using the nhs entity attributed to this object, it finds the matching DoS services from the db
        and filters the results"""

        # Check database for services with same first 5 digits of ODSCode
        matching_services = get_matching_dos_services(self.nhs_entity.ODSCode)
        logger.info(
            f"Found {len(matching_services)} services in DB with matching first 5 chars of ODSCode: {matching_services}"
        )

        # Filter for services with valid type and status
        self.matching_services = [
            s for s in matching_services if int(s.typeid) in VALID_SERVICE_TYPES and int(s.statusid) == VALID_STATUS_ID
        ]
        logger.info(
            f"Found {len(matching_services)} services with typeid in whitelist "
            f"{VALID_SERVICE_TYPES} and status id = {VALID_STATUS_ID}: {matching_services}"
        )
        return self.matching_services

    def get_change_requests(self) -> dict:
        """Generates change requests needed for the found services to make them inline with the NHS Entity

        Returns:
            dict: A dictionary of change requests
        """
        if self.matching_services is None:
            logger.error("Attempting to form change requests before matching "
                         "services have been found.")
            return

        change_requests = []
        for service in self.matching_services:

            # Find changes, don't make a change req if none found
            changes = get_changes(service, self.nhs_entity)
            if len(changes) > 0:
                cr = ChangeRequest(service.id, changes).get_change_request()
                change_requests.append(cr)

        logger.info(f"Created {len(change_requests)} change requests {dumps(change_requests, indent=2, default=str)}")

        # Assign to attribute and return
        self.change_requests = change_requests
        return self.change_requests

    def send_changes(self):
        """Sends change request payload off to next part of workflow
        [Which at the moment is straight to the next lambda]
        """
        if self.change_requests is None:
            logger.error("Attempting to send change requests before "
                         "get_change_requests have been called.")
            return

        for change_payload in self.change_requests:
            invoke_lambda_function(environ["EVENT_SENDER_LAMBDA_NAME"], change_payload)
            logger.info(f"Sent off change payload for id={change_payload['service_id']}")



def get_changes(dos_service: DoSService, nhs_entity: NHSEntity) -> dict:
        """Returns a dict of the changes that are required to get
           the service inline with the given nhs_entity.
        """
        changes = {}
        update_changes(changes, WEBSITE_CHANGE_KEY, dos_service.web, nhs_entity.Website)
        update_changes(changes, POSTCODE_CHANGE_KEY, dos_service.postcode, nhs_entity.Postcode)
        update_changes(changes, PHONE_CHANGE_KEY, dos_service.publicphone, nhs_entity.Phone)
        update_changes(changes, PUBLICNAME_CHANGE_KEY, dos_service.publicname, nhs_entity.OrganisationName)
        update_changes_with_address(changes, ADDRESS_CHANGE_KEY, dos_service.address, nhs_entity)
        update_changes_with_opening_times(changes, dos_service, nhs_entity)

        return changes


def update_changes(changes: dict, change_key: str, dos_value: str, nhs_uk_value: str):
    """Adds field to the change request if the field is not equal
    Args:
        changes (dict): Change Request changes
        change_key (str): Key to add to the change request
        dos_value (str): Field from the DoS database for comparision
        nhs_uk_value (str): NHS UK Entity value for comparision

    Returns:
        dict: Change Request changes
    """
    if str(dos_value) != str(nhs_uk_value):
        logger.debug(f"{change_key} is not equal, {dos_value=} != {nhs_uk_value=}")
        changes[change_key] = nhs_uk_value


def update_changes_with_address(changes: dict, change_key: str, 
    dos_address: str, nhs_uk_entity: NHSEntity) -> dict:
    """Adds the address to the change request if the address is not equal

    Args:
        changes (dict): Change Request changes
        change_key (str): Key to add to the change request
        dos_address (str): Address from the DoS database for comparision
        nhs_uk_entity (NHSEntity): NHS UK Entity for comparision

    Returns:
        dict: Change Request changes
    """
    nhs_uk_address_lines = [
        nhs_uk_entity.Address1,
        nhs_uk_entity.Address2,
        nhs_uk_entity.Address3,
        nhs_uk_entity.City,
        nhs_uk_entity.County,
    ]
    nhs_uk_address = [
        address for address in nhs_uk_address_lines if address is not None and address.strip() != ""]
    nhs_uk_address_string = "$".join(nhs_uk_address)
    if dos_address != nhs_uk_address_string:
        logger.debug(f"Address is not equal, {dos_address=} != {nhs_uk_address_string=}")
        changes[change_key] = nhs_uk_address
    return changes


def update_changes_with_opening_times(changes, dos_service: DoSService, nhs_entity: NHSEntity):

    # SPECIFIED OPENING TIMES
    dos_spec_open_dates = dos_service.specififed_opening_times()
    nhs_spec_open_dates = nhs_entity.get_specified_opening_times()
    if (len(dos_spec_open_dates) != len(nhs_spec_open_dates) or
        set(dos_spec_open_dates) != set(nhs_spec_open_dates)):

        changes[OPENING_DATES_KEY] = export_cr_format_spec_list(dos_spec_open_dates)

    # STANDARD OPENING TIMES
    dos_std_open_dates = dos_service.standard_opening_times()
    nhs_std_open_dates = nhs_entity.get_standard_opening_times()
    if dos_std_open_dates != nhs_std_open_dates:
        changes[OPENING_DAYS_KEY] = nhs_std_open_dates.export_cr_format()


@tracer.capture_lambda_handler()
@setup_logger
def lambda_handler(event, context):
    """Entrypoint handler for the event_receiver lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Event: The event payload should contain a NHS Entity (Service)

    Some code may need to be changed if the exact input format is changed.

    """

    for env_var in expected_env_vars:
        if env_var not in environ:
            err_msg = f"Environmental variable {env_var} not present"
            logger.error(err_msg)

    nhs_entity = NHSEntity(event)
    logger.info(f"Begun event processor function for NHS Entity: "
                f"{dumps(nhs_entity.__dict__, indent=2, default=str)}")

    event_processor = EventProcessor(nhs_entity)
    matching_services = event_processor.get_matching_services()

    if len(matching_services) == 0:
        logger.error(f"No matching DOS services found that fit all criteria "
                     f"for ODSCode '{nhs_entity.ODSCode}'")

    event_processor.get_change_requests()

    if is_mock_mode() is False:
        event_processor.send_changes()
    else:
        logger.info("Mock Mode on. Change requests will not be sent")
