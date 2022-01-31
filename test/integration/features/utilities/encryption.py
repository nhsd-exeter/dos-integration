# app.py
from aws_encryption_sdk import CommitmentPolicy, EncryptionSDKClient, StrictAwsKmsMasterKeyProvider

from boto3 import client

from os import environ


def initialise_encryption_client():

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

    return encrypt_string
