from boto3 import client
from botocore.exceptions import ClientError
from partiql import run_partiql, run_partiql_batch
from os import getenv

table_name = getenv("DYNAMO_DB_TABLE")


def dynamodb_cleanup_job():
    next_token = "Not None"
    total = 0
    while next_token is not None:
        # Get the next group of offending items
        select_sql = f'SELECT "Id", "ODSCode" FROM "{table_name}" WHERE "Event"."Staff" Is Not MISSING'
        if next_token == "Not None":
            results = run_partiql(select_sql)
        else:
            results = run_partiql(select_sql, next_token)

        items = results.get("Items", [])
        print(f"Retrieved {len(items)} items")
        next_token = results.get("NextToken", None)

        #
        if len(items) > 0:
            # Group the items into batches of 25
            batches = [items[i : i + 25] for i in range(0, len(items), 25)]

            for batch in batches:
                # Create the PartiQL statements and parameters
                statements = []
                params = []
                for item in batch:
                    statements.append(
                        f"""UPDATE "{table_name}" REMOVE "Event"."Staff" WHERE "Id" = ? AND "ODSCode" = ?"""
                    )
                    params.append([item["Id"], item["ODSCode"]])

                # Execute the batch
                run_partiql_batch(statements, params)
                total += len(batch)
                print(f"Updated {len(batch)} items")
                print(f"Total Updated: {total}")


if __name__ == "__main__":
    dynamodb_cleanup_job()
