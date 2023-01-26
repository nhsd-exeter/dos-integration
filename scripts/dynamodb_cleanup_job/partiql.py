from boto3 import resource
from botocore.exceptions import ClientError
from os import getenv


dyn_resource = resource("dynamodb")
dyn_resource.Table(getenv("DYNAMO_DB_TABLE"))


def run_partiql(statement: str, next_token: str = "") -> dict:
    try:
        if next_token:
            output = dyn_resource.meta.client.execute_statement(
                Statement=statement,
                NextToken=next_token,
            )
        else:
            output = dyn_resource.meta.client.execute_statement(Statement=statement)
    except ClientError as err:
        print(
            "Couldn't execute PartiQL '%s'. Here's why: %s: %s",
            statement,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    return output


def run_partiql_batch(statements, param_list):
    try:
        dyn_resource.meta.client.batch_execute_statement(
            Statements=[
                {"Statement": statement, "Parameters": params} for statement, params in zip(statements, param_list)
            ]
        )
    except ClientError as err:
        print(
            "Couldn't execute batch of PartiQL statements. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
