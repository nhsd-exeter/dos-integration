from json import loads, dumps
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Entrypoint handler for the authoriser lambda

    Args:
        event (Dict[str, Any]): Lambda function invocation event
        context (LambdaContext): Lambda function context object

    Returns:
        dict: Response to change request
    """
    event = loads(event["body"])
    print(event)
    change_request_response = {"dosChanges": []}
    counter = 1
    for row in event["changes"]:
        change_request_response["dosChanges"].append({"changeId": str(counter) * 9})
        counter += 1
    return {"statusCode": 200, "body": dumps(change_request_response)}
