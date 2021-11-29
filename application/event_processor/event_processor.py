from json import dumps
from logging import getLogger
from os import environ, getenv
import sys
sys.path.append("../")

from aws_lambda_powertools import Tracer
from boto3 import client

from change_request import ChangeRequest
from common.logger import setup_logger
from common.utilities import is_mock_mode, invoke_lambda_function
from dos import VALID_SERVICE_TYPES, VALID_STATUS_ID, get_matching_dos_services
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
            changes = service.get_changes(self.nhs_entity)
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
