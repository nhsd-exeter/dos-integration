from boto3 import client
from os import getenv

table_name = getenv("DYNAMO_DB_TABLE")


def dynamodb_cleanup_job():
    next_token = "Not None"
    dynamodb = client("dynamodb")
    count = 0
    total_count = 0
    while next_token is not None:
        if next_token == "Not None":
            results = dynamodb.scan(
                TableName=table_name,
                ProjectionExpression="Id,ODSCode",
                FilterExpression="attribute_exists(Event.Staff)",
                ConsistentRead=True,
            )
        else:
            results = dynamodb.scan(
                TableName=table_name,
                ProjectionExpression="Id,ODSCode",
                FilterExpression="attribute_exists(Event.Staff)",
                ConsistentRead=True,
                ExclusiveStartKey=next_token,
            )
        total_count += results["ScannedCount"]
        next_token = results.get("LastEvaluatedKey", None)
        items = results.get("Items", [])
        if len(items) > 0:
            count += results["Count"]
            for item in items:
                dynamodb.update_item(
                    TableName=table_name,
                    Key={"Id": item["Id"], "ODSCode": item["ODSCode"]},
                    UpdateExpression="REMOVE Event.Staff",
                )
            print(f"Updated {len(items)} items")
            print(f"Updated Total: {count}")
        print(f"Scanned Total: {total_count}")


if __name__ == "__main__":
    dynamodb_cleanup_job()
