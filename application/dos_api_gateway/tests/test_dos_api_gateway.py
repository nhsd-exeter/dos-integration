from json import dumps, loads

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from ..dos_api_gateway import lambda_handler


def test_lambda_handler():
    # Arrange
    change_request = {
        "reference": "1",
        "system": "DoS Integration",
        "message": "Test message 153181659229",
        "service_id": "49016",
        "changes": {"website": "https://www.google.pl", "public_name": "Test Name"},
    }
    lambda_event = {}
    lambda_event["body"] = dumps(change_request)
    context = LambdaContext()
    # Act
    response = lambda_handler(lambda_event, context)
    # Assert
    assert response["statusCode"] == 200
    assert loads(response["body"]) == {"dosChanges": [{"changeId": "1" * 9}, {"changeId": "2" * 9}]}
