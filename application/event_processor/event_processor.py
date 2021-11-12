from os import environ
import sys
import logging
from logging import getLogger
import json

import boto3
from aws_lambda_powertools import Tracer

from dos import get_matching_dos_services, valid_service_types, valid_status_id
from nhs import NHSEntity

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = getLogger("lambda")
tracer = Tracer()

lambda_client = boto3.client("lambda")


expected_env_vars = (
    "DB_SERVER",
    "DB_PORT",
    "DB_NAME",
    "DB_USER_NAME",
    "DB_SECRET_NAME",
    "EVENT_SENDER_LAMBDA_NAME"
    )


class EventProcessor:

    def __init__(self, nhs_entity):
        self.nhs_entity = nhs_entity
        self.matching_services = None
        self.change_requests = None


    def get_matching_services(self):

        # Check database for services with same first 5 digits of ODSCode
        matching_services = get_matching_dos_services(self.nhs_entity.odscode)
        log.info(f"Found {len(matching_services)} services in DB with matching "
                f"first 5 chars of ODSCode: {matching_services}")


        # Filter for services with valid type and status
        matching_services = [s for s in matching_services
                            if  int(s.typeid) in valid_service_types
                            and int(s.statusid) == valid_status_id]
        log.info(f"Found {len(matching_services)} services with typeid in whitelist "
                 f"{valid_service_types} and status id = {valid_status_id}: "
                 f"{matching_services}")


        # Assign result to attribute and return
        self.matching_services = matching_services
        return self.matching_services


    def get_change_requests(self):
        assert self.matching_services is not None

        # Generate change request for each service (if needed)
        change_requests = []
        for service in self.matching_services:

            # Find changes, skip if none found
            changes = service.get_changes(self.nhs_entity)
            if len(changes) == 0:
                continue

            # Construct Change Request
            trace_id = environ.get("_X_AMZN_TRACE_ID", default="<NO-TRACE-ID>")
            cr = {"reference": trace_id,
                  "system": "DoS Integration",
                  "message": f"AWS Lambda trace id: {trace_id}",
                  "service_id": service.id,
                  "changes": changes}

            change_requests.append(cr)


        log.info(f"Created {len(change_requests)} change requests\n"
                 f"{json.dumps(change_requests, indent=2, default=str)}")


        # Assign to attribute and return
        self.change_requests = change_requests
        return self.change_requests


    def send_changes(self):
        """ Sends change request payload off to next part of workflow
            Which at the moment is straight to the next lambda
            """

        assert self.change_requests is not None

        for change_payload in self.change_requests:
            resp = lambda_client.invoke(FunctionName=environ["EVENT_SENDER_LAMBDA_NAME"],
                                        InvocationType="Event",
                                        Payload=change_payload)
            log.info(f"Sent off change payload for id={change_payload['service_id']}\n{resp}")





@tracer.capture_lambda_handler()
def lambda_handler(event, context):

    # Check all required env vars are present
    for env_var in expected_env_vars:
        if env_var not in environ:
            err_msg = f"Environmental variable {env_var} not present"
            log.error(err_msg)
            return {"statusCode": 400, "error": err_msg}


    # It's assumed currently that a pharmacy (NHS Entity) will
    # be passed in through the event. The start here may need 
    # to be edited slightly depending on its exact form of the 
    # payload
    nhs_entity = NHSEntity(event["entity"])
    log.info(f"Begun event processor function for NHS Entity\n"
             f"{json.dumps(nhs_entity.__dict__, indent=2, default=str)}")


    event_processor = EventProcessor(nhs_entity)
    matching_services = event_processor.get_matching_services()

    # IF NO MATCHING SERVICES FOUND - log error and return/end
    if len(matching_services) == 0:
        err_msg = (f"No matching DOS services found that fit all criteria for "
                   f"ODSCode '{nhs_entity.odscode}'")
        log.error(err_msg)
        return {"statusCode": 400, "error": err_msg}

    
    change_requests = event_processor.get_change_requests()


    if event.get("send_changes", False) is True:
        event_processor.send_changes()
    else:
        log.info(f"'send_changes' argument in event payload is set to False. "
                 f"Change requests will not be sent")
    

    return {
        "statusCode": 200, 
        "body": {
            "matching_services": [s.__dict__ for s in matching_services],
            "change_requests": change_requests
            }
        }
