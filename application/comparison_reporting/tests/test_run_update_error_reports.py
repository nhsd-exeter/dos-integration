from unittest.mock import patch

from common.tests.conftest import dummy_dos_service, get_std_event


@patch("application.comparison_reporting.reporter.Reporter")
@patch("application.common.dos.get_services_from_db")
@patch("application.common.dynamodb.get_newest_event_per_odscode")
def test_run_update_error_reports(
        mock_get_newest_event_per_odscode,
        mock_get_services_from_db,
        mock_Reporter):

    mock_get_services_from_db.return_value = [dummy_dos_service() for i in range(10)]
    mock_get_newest_event_per_odscode.return_value = {
        "FAT91": {
            "ODSCOde": "FAT91",
            "Event": get_std_event(ODSCode="FAT91")
        },
        "BIL92": {
            "ODSCOde": "BIL92",
            "Event": get_std_event(ODSCode="BIL92")
        }
    }
