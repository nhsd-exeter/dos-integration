# Run from application/ dir using below command
# python3 -m comparison_reporting.run_update_error_reports
from os import path
from pathlib import Path

from comparison_reporting.reporter import Reporter

from common.constants import DENTIST_SERVICE_TYPE_IDS, PHARMACY_SERVICE_TYPE_IDS
from common.dos import get_services_from_db
from common.dynamodb import get_newest_event_per_odscode
from common.nhs import NHSEntity


def run_update_error_reports(output_dir: str = "reports_output/"):
    service_type_ids = PHARMACY_SERVICE_TYPE_IDS + DENTIST_SERVICE_TYPE_IDS
    dos_services = get_services_from_db(service_type_ids)
    most_recent_events = get_newest_event_per_odscode()
    nhs_entities = [NHSEntity(item["Event"]) for item in most_recent_events if "Event" in item]
    reporter = Reporter(nhs_entities, dos_services)
    reporter.run_and_save_reports(file_prefix="Update_err_reports_", output_dir=output_dir)


if __name__ == "__main__":
    run_update_error_reports(path.join(Path.home(), "reports_output"))
