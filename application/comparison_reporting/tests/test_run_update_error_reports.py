from unittest.mock import patch

from comparison_reporting.run_update_error_reports import run_update_error_reports

from common.tests.conftest import dummy_dos_service, get_std_event


@patch("application.common.dynamodb.get_newest_event_per_odscode")
@patch("application.common.dos.get_services_from_db")
@patch("application.comparison_reporting.reporter.Reporter")
def test_run_update_error_reports(
        mock_get_newest_event_per_odscode,
        mock_get_services_from_db,
        mock_Reporter,
        mock_run_and_save_reports):

    mock_get_services_from_db.side_effect = [dummy_dos_service() for i in range(10)]
    mock_get_newest_event_per_odscode.side_effect = {
        "FAT91": {
            "ODSCOde": "FAT91",
            "Event": get_std_event(ODSCode="FAT91")
        },
        "BIL92": {
            "ODSCOde": "BIL92",
            "Event": get_std_event(ODSCode="BIL92")
        }
    }

    run_update_error_reports()
    mock_Reporter.assert_called()
    mock_Reporter.run_and_save_reports.assert_called()
