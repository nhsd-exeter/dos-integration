from os import environ
from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext
from logging import getLogger
import json

import boto3
from aws_lambda_powertools import Tracer

from event_processor.dos import get_matching_dos_services, valid_service_types, valid_status_id
from event_processor.nhs import NHSEntity
from common.logger import setup_logger

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = getLogger("lambda")
tracer = Tracer()

lambda_client = boto3.client("lambda", region_name="eu-west-2")


expected_env_vars = ("DB_SERVER", "DB_PORT", "DB_NAME", "DB_USER_NAME", "EVENT_SENDER_LAMBDA_NAME")


class EventProcessor:
    def __init__(self, nhs_entity):
        self.nhs_entity = nhs_entity

        # Set these values to None to show they are yet to be calculated
        self.matching_services = None
        self.change_requests = None

    def get_matching_services(self):
        """Using the nhs entity attributed to this object, it finds the
        matching DoS services from the db and filters the results"""

        # Check database for services with same first 5 digits of OdsCode
        matching_services = get_matching_dos_services(self.nhs_entity.OdsCode)
        log.info(
            f"Found {len(matching_services)} services in DB with matching "
            f"first 5 chars of OdsCode: {matching_services}"
        )

        # Filter for services with valid type and status
        matching_services = [
            s for s in matching_services if int(s.typeid) in valid_service_types and int(s.statusid) == valid_status_id
        ]
        log.info(
            f"Found {len(matching_services)} services with typeid in whitelist "
            f"{valid_service_types} and status id = {valid_status_id}: "
            f"{matching_services}"
        )

        # Assign result to attribute and return
        self.matching_services = matching_services
        return self.matching_services

    def get_change_requests(self):
        """Generates change requests needed for the found services to
        make them inline with the NHS Entity
        """

        assert self.matching_services is not None, "Matching services not yet calculated"

        change_requests = []
        for service in self.matching_services:

            # Find changes, don't make a change req if none found
            changes = service.get_changes(self.nhs_entity)
            if len(changes) == 0:
                continue

            # Construct Change Request
            trace_id = environ.get("_X_AMZN_TRACE_ID", default="<NO-TRACE-ID>")
            cr = {
                "reference": trace_id,
                "system": "DoS Integration",
                "message": f"DoS Integration CR. AMZN-trace-id: {trace_id}",
                "service_id": service.id,
                "changes": changes,
            }

            change_requests.append(cr)

        log.info(
            f"Created {len(change_requests)} change requests\n" f"{json.dumps(change_requests, indent=2, default=str)}"
        )

        # Assign to attribute and return
        self.change_requests = change_requests
        return self.change_requests

    def send_changes(self):
        """Sends change request payload off to next part of workflow
        Which at the moment is straight to the next lambda
        """

        assert self.change_requests is not None

        for change_payload in self.change_requests:
            resp = lambda_client.invoke(
                FunctionName=environ["EVENT_SENDER_LAMBDA_NAME"], InvocationType="Event", Payload=change_payload
            )
            log.info(f"Sent off change payload for id={change_payload['service_id']}\n{resp}")


@tracer.capture_lambda_handler()
@setup_logger
def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    """

    event: The event payload should contain a "entity" field which
        contains the fields for the NHS Entity (Pharmacy)

        example
        {"send_changes: False,
        "entity":
            {"OdsCode": "FA0021"
            "publicphone": "893233284932",
            "etc": "some data"
            "another field": "more data"}}
            etc etc...

            Some code may need to be changed if the exact
            input format is changed.

            Another optional field 'send_changes' will decide if the
            change requests generated will be sent at the end.  (def: False)

    """

    # Check all required env vars are present
    for env_var in expected_env_vars:
        if env_var not in environ:
            err_msg = f"Environmental variable {env_var} not present"
            log.error(err_msg)
            return {"statusCode": 400, "error": err_msg}

    # Create NHS Entity object (the pharmacy)
    nhs_entity = NHSEntity(event)
    log.info(
        f"Begun event processor function for NHS Entity\n" f"{json.dumps(nhs_entity.__dict__, indent=2, default=str)}"
    )

    # Create processor using our NHS Entity
    event_processor = EventProcessor(nhs_entity)
    matching_services = event_processor.get_matching_services()

    # IF NO MATCHING SERVICES FOUND - log error and return/end
    if len(matching_services) == 0:
        err_msg = f"No matching DOS services found that fit all criteria for " f"OdsCode '{nhs_entity.OdsCode}'"
        log.error(err_msg)
        return {"statusCode": 400, "error": err_msg}

    # Generate the change requests (if any are needed)
    change_requests = event_processor.get_change_requests()

    # Either send off the change requests or not depending on option
    if event.get("send_changes", False) is True:
        event_processor.send_changes()
    else:
        log.info("'send_changes' argument in event payload is set to False. Change requests will not be sent")

    # Return the matching services found, as well as the change requests
    # in json format
    return {
        "statusCode": 200,
        "body": json.dumps({"change_requests": change_requests}),
    }
