from json import dumps


def lambda_handler(event, context):
    return {"statusCode": 200, "body": dumps({"Message": "Lambda received message"})}
