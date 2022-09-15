from os import environ
from unittest.mock import patch

from application.common.s3 import put_email_to_s3

FILE_PATH = "application.common.s3"


@patch(f"{FILE_PATH}.resource")
def test_put_email_to_s3(mock_resource):
    # Arrange
    environ["SEND_EMAIL_BUCKET_NAME"] = bucket_name = "bucket_name"
    local_filename = "local_filename"
    s3_filename = "s3_filename"
    # Act
    put_email_to_s3(local_filename, s3_filename)
    # Assert
    mock_resource.assert_called_once_with("s3")
    mock_resource.return_value.meta.client.upload_file.assert_called_once_with(local_filename, bucket_name, s3_filename)
    # Cleanup
    del environ["SEND_EMAIL_BUCKET_NAME"]
