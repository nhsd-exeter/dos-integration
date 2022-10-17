from unittest.mock import patch

from comparison_reporting.run_update_error_reports import run_update_error_reports

from common.nhs import NHSEntity
from common.tests.conftest import dummy_dos_service, get_std_event

FILE_PATH = "comparison_reporting.run_update_error_reports"


@patch(f"{FILE_PATH}.Reporter")
@patch(f"{FILE_PATH}.get_services_from_db")
@patch(f"{FILE_PATH}.get_newest_event_per_odscode")
@patch(f"{FILE_PATH}.get_all_valid_dos_postcodes")
def test_run_update_error_reports(
        mock_get_all_valid_dos_postcodes,
        mock_get_newest_event_per_odscode,
        mock_get_services_from_db,
        mock_Reporter):

    valid_postcodes = {"SG68PQ", "HY79PH"}
    dos_services = [dummy_dos_service() for i in range(10)]
    newest_events = {
        "FAT91": {
            "ODSCOde": "FAT91",
            "Event": get_std_event(ODSCode="FAT91")
        },
        "BIL92": {
            "ODSCOde": "BIL92",
            "Event": get_std_event(ODSCode="BIL92")
        }
    }
    nhs_entities = [NHSEntity(item["Event"]) for item in newest_events.values()]

    mock_get_all_valid_dos_postcodes.return_value = valid_postcodes
    mock_get_services_from_db.return_value = dos_services
    mock_get_newest_event_per_odscode.return_value = newest_events

    output_dir = "test_dir"
    run_update_error_reports(output_dir=output_dir)
    mock_Reporter.assert_called_once_with(
        nhs_entities=nhs_entities,
        dos_services=dos_services,
        valid_dos_postcodes=valid_postcodes)
