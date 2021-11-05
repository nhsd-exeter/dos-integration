from unittest.mock import patch

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext

from ..event_sender import lambda_handler

CHANGE_REQUEST = {
    "reference": "1",
    "system": "Profile Updater (test)",
    "message": "Test message 1531816592293|@./",
    "service_id": "49016",
    "changes": {"ods_code": "f0000", "phone": "0118 999 88199 9119 725 3", "website": "https://www.google.pl"},
}

FILE_PATH = "application.event_sender.event_sender"


@patch(f"{FILE_PATH}.ChangeRequest")
def test_lambda_handler(mock_change_request):
    # Arrange
    context = LambdaContext()
    context._function_name = "test"
    context._aws_request_id = "test"
    # Act
    lambda_handler(CHANGE_REQUEST, context)
    # Assert
    mock_change_request.assert_called_once_with(CHANGE_REQUEST)
    mock_change_request().post_change_request.assert_called_once_with()
