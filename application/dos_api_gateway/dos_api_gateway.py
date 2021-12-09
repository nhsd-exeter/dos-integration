from json import loads, dumps
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

logger = Logger()


@logger.inject_lambda_context(correlation_id_path="headers.x_correlation_id")
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Returns:
        dict: Response to change request
    """
    event = loads(event["body"])
    change_request_response = {"dosChanges": []}
    logger.info("MOCK DoS API Gateway - Change request received", extra={"change_event": event})
    counter = 1
    for row in event["changes"]:
        change_request_response["dosChanges"].append({"changeId": str(counter) * 9})
        counter += 1
    return {"statusCode": 200, "body": dumps(change_request_response)}
