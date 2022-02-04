from aws_encryption_sdk import CommitmentPolicy, EncryptionSDKClient, StrictAwsKmsMasterKeyProvider
from aws_lambda_powertools import Logger
from boto3 import client
from os import environ

logger = Logger(child=True)


class MessageEncryptionHelper:
    """Class to represent a MessageEncryptionHelper"""

    def __init__(self) -> None:

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
        self._encryption_client = EncryptionSDKClient(
            commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_REQUIRE_DECRYPT
        )

        # Create an AWS KMS master key provider
        kms_kwargs = dict(key_ids=[key_arn])

        self._master_key_provider = StrictAwsKmsMasterKeyProvider(**kms_kwargs)

    def encrypt_string(self, plaintext):
        encrypted_text, encryptor_header = self._encryption_client.encrypt(
            source=plaintext, key_provider=self._master_key_provider
        )
        return encrypted_text

    def decrypt_string(self, ciphertext):

        decrypted_text, encryptor_header = self._encryption_client.decrypt(
            source=ciphertext, key_provider=self._master_key_provider
        )
        return decrypted_text.decode()
