# Run from application/ dir using below command
# python3 -m comparison_reporting.run_update_error_reports
from os import path
from pathlib import Path

from comparison_reporting.reporter import Reporter
from common.dos import get_services_from_db
from common.nhs import NHSEntity
from common.dynamodb import get_most_recent_events
from common.constants import PHARMACY_SERVICE_TYPE_IDS, DENTIST_SERVICE_TYPE_IDS


def run_update_error_reports(output_dir: str = "reports_out/", small_sample: bool = False):
    dos_services = get_services_from_db(PHARMACY_SERVICE_TYPE_IDS + DENTIST_SERVICE_TYPE_IDS)
    most_recent_events = get_most_recent_events(max_pages=(5 if small_sample else None))
    nhs_entities = [NHSEntity(item["Event"]) for item in most_recent_events.values()]
    reporter = Reporter(nhs_entities, dos_services)
    reporter.run_and_save_reports(file_prefix="Update_err_reports_", output_dir=output_dir)


if __name__ == "__main__":
    output_dir = path.join(Path.home(), "reports_output")
    run_update_error_reports(output_dir, True)
