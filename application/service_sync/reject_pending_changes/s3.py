from os import getenv

from aws_lambda_powertools.logging import Logger
from boto3 import client

logger = Logger(child=True)


def put_content_to_s3(content: bytes, s3_filename: str) -> None:
    """Upload a file contents to S3.

    Args:
        content (bytes): File contents
        s3_filename (str): The filename when the file is stored in S3
    """
    bucket = getenv("SEND_EMAIL_BUCKET_NAME")
    client("s3").put_object(Body=content, Bucket=bucket, Key=s3_filename, ServerSideEncryption="AES256")
    logger.info(
        f"Uploaded to S3 as {s3_filename}",
        extra={"bucket": bucket, "s3_filename": s3_filename},
    )
