from common.dos import get_services_from_db
from common.constants import DENTIST_SERVICE_TYPE_IDS
from reporting import get_dentists, Reporter


def run_dentist_reports():

    nhsuk_dentists = get_dentists()
    dentist_dos_services = get_services_from_db(DENTIST_SERVICE_TYPE_IDS)
    reporter = Reporter(nhs_entities=nhsuk_dentists, dos_services=dentist_dos_services)
    reporter.create_postcode_comparison_report("dentists_postcode_comparison_report.csv")
    reporter.create_std_opening_times_comparison_report("dentists_standard_opening_times_comparison_report.csv")
    reporter.create_spec_opening_times_comparison_report("dentists_specified_opening_times_comparison_report.csv")
    reporter.create_invalid_postcode_report("dentists_invalid_postcode_report.csv")
    reporter.create_invalid_spec_opening_times_report("dentists_invalid_spec_opening_times_report.csv")
    reporter.create_invalid_std_opening_times_report("dentists_invalid_std_opening_times_report.csv")


if __name__ == "__main__":
    run_dentist_reports()
