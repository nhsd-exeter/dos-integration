from json import loads, dumps
from os import getenv
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from time import sleep

logger = Logger()


@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Returns:
        dict: Response to change request
    """
    logger.info("Event Received", extra={"event": event})
    change_request = loads(event["body"])
    sleep(1.7)
    if change_request == {}:
        logger.warning("Empty change request received, likely a health check")
        return {"statusCode": 200, "body": "Change Request is empty"}

    correlation_id = change_request["reference"]
    logger.set_correlation_id(correlation_id)
    logger.info("MOCK DoS API Gateway - Change request received", extra={"change_request": event})

    if "bad request" in correlation_id.lower():
        logger.warning("MOCK DoS API Gateway - Returning Fake Bad Request", extra={"change_request": event})
        return {"statusCode": 400, "body": "Fake Bad Request trigged by correlation-id"}

    if getenv("CHAOS_MODE") == "true":
        logger.warning("CHAOS MODE ENABLED - Returning a 500 response")
        return {"statusCode": 500, "body": "Chaos mode is enabled"}

    change_request_response = {"dosChanges": []}

    if "changes" in change_request:
        counter = 1
        for row in change_request["changes"]:
            change_request_response["dosChanges"].append({"changeId": str(counter) * 9})
            counter += 1
    return {"statusCode": 201, "body": dumps(change_request_response)}
