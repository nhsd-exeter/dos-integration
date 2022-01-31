from aws_encryption_sdk import CommitmentPolicy, EncryptionSDKClient, StrictAwsKmsMasterKeyProvider
from aws_encryption_sdk.exceptions import (
    MaxEncryptedDataKeysExceeded,
    NotSupportedError,
    SerializationError,
    UnknownIdentityError,
)
from aws_lambda_powertools import Logger
from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from base64 import b64decode
from binascii import Error as binasciiError
from boto3 import client
from json import loads, dumps
from os import environ
from time import time
from typing import Any, Dict

from common.utilities import extract_body

logger = Logger(child=True)

SIGNING_KEY_KEY = "signing_key"
BAD_REQUEST = {"statusCode": 400, "body": dumps({"message": "Invalid payload"})}


def initialise_encryption_client():

    logger.info("Getting key")
    kms = client("kms")
    response = kms.describe_key(
        KeyId=f"alias/{environ['KEYALIAS']}",
        GrantTokens=[
            "string",
        ],
    )
    # Use the key arn you obtained in the previous step
    key_arn = response["KeyMetadata"]["Arn"]
    encryption_client = EncryptionSDKClient(commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT)

    # Create an AWS KMS master key provider
    kms_kwargs = dict(key_ids=[key_arn])

    master_key_provider = StrictAwsKmsMasterKeyProvider(**kms_kwargs)

    def encrypt_string(plaintext):

        encrypted_text, encryptor_header = encryption_client.encrypt(source=plaintext, key_provider=master_key_provider)
        return encrypted_text

    def decrypt_string(ciphertext):

        decrypted_text, encryptor_header = encryption_client.decrypt(
            source=ciphertext, key_provider=master_key_provider
        )
        return decrypted_text.decode()

    return encrypt_string, decrypt_string


def validate_signing_key(signing_key: Any, body: Dict[str, Any]) -> bool:
    try:
        encrypt_string, decrypt_string = initialise_encryption_client()
        decoded_key = b64decode(signing_key)
        data = loads(decrypt_string(decoded_key))
        assert data["ods_code"] == body["ods_code"], "Signing key invalid, ods code doesnt match"
        assert (
            data["dynamo_record_id"] == body["dynamo_record_id"]
        ), "Signing key invalid, dynamo_record_id code doesnt match"
        assert (
            data["message_received"] == body["message_received"]
        ), "Signing key invalid, message_received code doesnt match"
        assert data["time"] > time() - 86400, "Message was signed over 24 hours ago so ignoring"
        logger.info("Signing key validated")
        return True
    except (
        binasciiError,
        TypeError,
        AssertionError,
        MaxEncryptedDataKeysExceeded,
        NotSupportedError,
        SerializationError,
        UnknownIdentityError,
    ):
        logger.exception("Validation failed")
        return False


@lambda_handler_decorator(trace_execution=True)
def validate_event_is_signed(handler, event, context: LambdaContext):
    logger.info("Validating signing key")
    body = extract_body(event["body"])
    if SIGNING_KEY_KEY not in body:
        logger.error("No signing key in body")
        return BAD_REQUEST
    signing_key = body[SIGNING_KEY_KEY]
    is_valid = validate_signing_key(signing_key, body)
    if is_valid:
        response = handler(event, context)
        return response
    else:
        return BAD_REQUEST
