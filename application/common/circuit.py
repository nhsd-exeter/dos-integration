from os import environ

from aws_lambda_powertools.logging.logger import Logger
from boto3 import client
from boto3.dynamodb.types import TypeSerializer

from common.errors import DynamoDBError

logger = Logger(child=True)
dynamodb = client("dynamodb", region_name=environ["AWS_REGION"])


def put_circuit_is_open(circuit: str, is_open: bool) -> None:
    """Set the circuit open status for a given circuit.

    Args:
        circuit (str): Name of the circuit
        is_open (bool): boolean as to whether the circuit is open/True (broken) or closed/False (ok)
    """
    dynamo_record = {
        "Id": circuit,
        "ODSCode": "CIRCUIT",
        "IsOpen": is_open,
    }
    try:
        serializer = TypeSerializer()
        put_item = {k: serializer.serialize(v) for k, v in dynamo_record.items()}
        response = dynamodb.put_item(TableName=environ["CHANGE_EVENTS_TABLE_NAME"], Item=put_item)
        logger.info("Put circuit status", extra={"response": response, "item": put_item})
    except Exception as err:  # noqa: BLE001
        msg = f"Unable to set circuit '{circuit}' to open."
        raise DynamoDBError(msg) from err


def get_circuit_is_open(circuit: str) -> bool | None:
    """Gets the open status of a given circuit.

    Args:
        circuit (str): Name of the circuit

    Returns:
        Union[bool, None]: returns the status or None if the circuit does not exist.
    """
    try:
        respone = dynamodb.get_item(
            TableName=environ["CHANGE_EVENTS_TABLE_NAME"],
            Key={
                "Id": {
                    "S": circuit,
                },
                "ODSCode": {
                    "S": "CIRCUIT",
                },
            },
        )
        item = respone.get("Item")
        logger.debug(f"Circuit '{circuit}' is_open resp={item}")
        return None if item is None else bool(item["IsOpen"]["BOOL"])

    except Exception as err:  # noqa: BLE001
        msg = f"Unable to get circuit status for '{circuit}'."
        raise DynamoDBError(msg) from err
