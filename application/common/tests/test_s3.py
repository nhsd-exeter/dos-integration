from os import environ
from unittest.mock import patch

from application.common.s3 import put_content_to_s3

FILE_PATH = "application.common.s3"


@patch(f"{FILE_PATH}.client")
def test_put_content_to_s3(mock_client):
    # Arrange
    environ["SEND_EMAIL_BUCKET_NAME"] = bucket_name = "bucket_name"
    s3_filename = "s3_filename"
    content = b"content"
    # Act
    put_content_to_s3(content, s3_filename)
    # Assert
    mock_client.assert_called_once_with("s3")
    mock_client.return_value.put_object.assert_called_once_with(
        Body=content, Bucket=bucket_name, Key=s3_filename, ServerSideEncryption="AES256",
    )
    # Cleanup
    del environ["SEND_EMAIL_BUCKET_NAME"]
