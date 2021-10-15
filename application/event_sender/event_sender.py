from typing import Any, Dict
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: Dict[str, Any], context: LambdaContext):
    """[summary]

    Args:
        event (Dict[str, Any]): [description]
        context (LambdaContext): [description]
    """
    print("Hello World")


if __name__ == "__main__":
    lambda_handler(None, None)
