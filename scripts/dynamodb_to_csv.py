import boto3
import pandas as pd

TABLE_NAME = "DATA_CLONE_NAME"
OUTPUT_KEY = "export.csv"

dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(TABLE_NAME)

response = table.scan(IndexName="gsi_ods_sequence", Select="ALL_ATTRIBUTES")
data = response["Items"]
while "LastEvaluatedKey" in response:
    response = table.scan(
        ExclusiveStartKey=response["LastEvaluatedKey"], IndexName="gsi_ods_sequence", Select="ALL_ATTRIBUTES"
    )
    data.extend(response["Items"])

dataframe = pd.DataFrame(data)
dataframe.to_csv(OUTPUT_KEY, index=False, header=True)
