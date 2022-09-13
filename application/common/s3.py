from os import getenv

from aws_lambda_powertools.logging import Logger
from boto3 import resource

logger = Logger(child=True)


def put_email_to_s3(local_filename: str, s3_filename: str) -> None:
    """Puts an email to S3

    Args:
        local_file_name (str): The filename to find in the local filesystem
        s3_file_name (str): The filename when the file is stored in S3
    """
    s3 = resource("s3")
    bucket = getenv("SEND_EMAIL_BUCKET_NAME")
    s3.meta.client.upload_file(local_filename, bucket, s3_filename)
    logger.info(
        f"Uploaded {local_filename} to S3 as {s3_filename}",
        extra={"local_filename": local_filename, "bucket": bucket, "s3_filename": s3_filename},
    )
