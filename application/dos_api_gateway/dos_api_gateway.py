from json import loads, dumps
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

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
    change_event = loads(event["body"])
    correlation_id = change_event["reference"]
    logger.set_correlation_id(correlation_id)
    if "bad request" in correlation_id.lower():
        logger.info("Bad Request  - MOCK DoS API Gateway - Returning Fake Bad Request", extra={"change_request": event})
        return {"statusCode": 400, "body" : "Fake Bad Request trigged by correlation-id"}

    change_request_response = {"dosChanges": []}
    logger.info("MOCK DoS API Gateway - Change request received", extra={"change_request": event})
    counter = 1
    for row in change_event["changes"]:
        change_request_response["dosChanges"].append({"changeId": str(counter) * 9})
        counter += 1
    return {"statusCode": 200, "body": dumps(change_request_response)}
