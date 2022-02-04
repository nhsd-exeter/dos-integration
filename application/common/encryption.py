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
from json import loads, dumps
from time import time
from typing import Any, Dict, Union
from common.encryption_helper import MessageEncryptionHelper

from common.utilities import extract_body

logger = Logger(child=True)

SIGNING_KEY_KEY = "signing_key"
BAD_REQUEST = {"statusCode": 400, "body": dumps({"message": "Invalid payload"})}
helper: Union[MessageEncryptionHelper, None] = None


def initialise_encryption_client() -> MessageEncryptionHelper:
    global helper
    if helper is None:
        helper = MessageEncryptionHelper()
    return helper


def validate_signing_key(signing_key: Any, body: Dict[str, Any]) -> bool:
    try:
        helper = initialise_encryption_client()
        decoded_key = b64decode(signing_key)
        data = loads(helper.decrypt_string(decoded_key))
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
