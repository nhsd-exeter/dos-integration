import sys
from os.path import join
from pathlib import Path

sys.path.insert(1, join(Path().absolute().parent.parent, "application"))
from common.constants import DENTIST_SERVICE_TYPE_IDS, PHARMACY_SERVICE_TYPE_IDS
from common.dos import get_all_valid_dos_postcodes, get_services_from_db
from common.dynamodb import get_newest_event_per_odscode
from common.nhs import NHSEntity

from reporter import Reporter


def run_update_error_reports(output_dir: str = "reports_output/"):
    most_recent_events = get_newest_event_per_odscode()
    service_type_ids = PHARMACY_SERVICE_TYPE_IDS + DENTIST_SERVICE_TYPE_IDS
    dos_services = get_services_from_db(service_type_ids)
    valid_dos_postcodes = get_all_valid_dos_postcodes()
    newest_nhs_entities = [NHSEntity(item["Event"]) for item in most_recent_events.values() if "Event" in item]
    reporter = Reporter(
        nhs_entities=newest_nhs_entities,
        dos_services=dos_services,
        valid_dos_postcodes=valid_dos_postcodes)
    reporter.run_and_save_reports(file_prefix="Update_err_reports_", output_dir=output_dir)


if __name__ == "__main__":  # pragma: no cover
    run_update_error_reports(join(Path.home(), "reports_output"))
