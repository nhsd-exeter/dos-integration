from json import dumps
from typing import Any, Dict


def set_return_value(status_code: int, message: str) -> Dict[str, Any]:
    """Sets the standard return value for the lambda function

    Args:
        status_code (int): Status code for response
        message (str): Message for response

    Returns:
        Dict[str, Any]: A formatted response
    """
    return {"statusCode": status_code, "body": dumps({"message": message})}


def set_error_return_value(status_code: int, message: str) -> Dict[str, Any]:
    """Sets the error return value for the lambda function

    Args:
        status_code (int): Status code for response
        message (str): Message for response

    Returns:
        Dict[str, Any]: A formatted error response
    """
    return {"statusCode": status_code, "errorMessage": dumps({"message": message})}
