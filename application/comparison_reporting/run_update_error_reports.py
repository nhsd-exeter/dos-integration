# Run from application/ dir using below command
# python3 -m comparison_reporting.run_update_error_reports
from os import environ
import sys
from pathlib import Path
import boto3
from pprint import pprint as pp

from comparison_reporting.reporter import Reporter
from common.dos import get_services_from_db
from common.nhs import NHSEntity
from common.constants import PHARMACY_SERVICE_TYPE_IDS



ddb_table = boto3.resource("dynamodb").Table(environ["CHANGE_EVENTS_TABLE_NAME"])

def get_most_recent_nhs_entity_update(sample: bool = False):

    # Get all items from DDB
    resp = ddb_table.scan()
    data = resp.get("Items")
    while "LastEvaluatedKey" in resp and not sample:
        resp = ddb_table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        data.extend(resp["Items"])
    
    # Find the most recent entry of each odscode present
    most_recent_events = {}
    for item in data:
        odscode = item["ODSCode"]
        try:
            if most_recent_events[odscode]["SequenceNumber"] < item["SequenceNumber"]:
                most_recent_events[odscode] = item
        except KeyError:
            most_recent_events[odscode] = item

    # Retunr NHSEntity objects
    nhs_entities = [NHSEntity(item["Event"]) for item in most_recent_events.values()]
    return nhs_entities


dos_services = get_services_from_db(typeids=PHARMACY_SERVICE_TYPE_IDS)
nhs_entities = get_most_recent_nhs_entity_update(sample=True)


reporter = Reporter(nhs_entities, dos_services)

reporter.run_and_save_reports(file_prefix="Update_err_reports_", output_dir=f"{Path.home()}/report_out")


