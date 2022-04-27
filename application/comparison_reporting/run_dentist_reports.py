from datetime import datetime
from itertools import groupby
from collections import defaultdict
from typing import List

from aws_lambda_powertools import Logger

from common.dos import get_services_from_db
from common.nhs import NHSEntity
from common.opening_times import OpenPeriod, StandardOpeningTimes, SpecifiedOpeningTime
from common.constants import DENTIST_SERVICE_TYPE_IDS
from reporting import Reporter, download_csv_as_dicts


logger = Logger(child=True)
DENTIST_DATA_FILE_URL = "https://assets.nhs.uk/data/foi/Dentists.csv"
DENTIST_OPENING_TIMES_DATA_FILE_URL = "https://assets.nhs.uk/data/foi/DentistOpeningTimes.csv"


def get_dentists() -> List[NHSEntity]:
    """Downloads the current NHS UK dentist data from https://www.nhs.uk/about-us/nhs-website-datasets/
    and returns them as a list of NHSEntity objects"""

    dentists_data = download_csv_as_dicts(DENTIST_DATA_FILE_URL, delimiter="¬")
    dentists_open_times_data = download_csv_as_dicts(DENTIST_OPENING_TIMES_DATA_FILE_URL, delimiter="¬")

    # Extract and sort opening times data items
    std_open_data = defaultdict(list)
    spec_open_data = defaultdict(list)
    for item in dentists_open_times_data:
        id = item["OrganisationId"]
        opening_type = item["OpeningTimeType"]
        if opening_type == "General":
            std_open_data[id].append(item)
        elif opening_type == "Additional":
            spec_open_data[id].append(item)
        else:
            logger.warning(f"Unknown opening type '{opening_type}'.")

    # Initialise dentists as NHS Entity objects
    dentists = []
    for entity_data in dentists_data:
        id = entity_data.get("OrganisationID")

        nhs_entity = NHSEntity({})
        nhs_entity.odscode = entity_data.get("OrganisationCode")
        nhs_entity.org_name = entity_data.get("OrganisationName")
        nhs_entity.org_type = entity_data.get("OrganisationType")
        nhs_entity.org_sub_type = entity_data.get("SubType")
        nhs_entity.org_status = entity_data.get("OrganisationStatus")
        nhs_entity.postcode = entity_data.get("Postcode")
        nhs_entity.parent_org_name = entity_data.get("ParentName")
        nhs_entity.city = entity_data.get("City")
        nhs_entity.county = entity_data.get("County")
        nhs_entity.address_lines = [
            line
            for line in [entity_data.get(x) for x in [f"Address{i}" for i in range(1, 5)] + ["City", "County"]]
            if isinstance(line, str) and line.strip() != ""
        ]
        nhs_entity.phone = entity_data.get("Phone")
        nhs_entity.website = entity_data.get("Website")
        nhs_entity.standard_opening_times = StandardOpeningTimes()
        nhs_entity.specified_opening_times = []

        # Add std opening times to the dentist
        for std_open_period in std_open_data.get(id, []):
            is_open = std_open_period["IsOpen"].upper()
            if is_open == "TRUE":
                day = std_open_period["WeekDay"].lower()
                open_period = OpenPeriod.from_string(std_open_period["Times"])
                nhs_entity.standard_opening_times.add_open_period(open_period, day)
            elif is_open == "FALSE":
                logger.warning("A general weekday opening time IsOpen value is FALSE")

        # Add spec opening times to the dentist
        date_grouping = groupby(
            spec_open_data.get(id, []),
            lambda k: datetime.strptime(k["AdditonalOpeningDate"], "%b  %d  %Y").date()
        )
        for date, open_period_items in date_grouping:

            is_open = True
            open_periods = []
            for item in list(open_period_items):
                if item["IsOpen"].upper() == "TRUE":
                    open_periods.append(OpenPeriod.from_string(item["Times"]))
                else:
                    is_open = False
            nhs_entity.specified_opening_times.append(SpecifiedOpeningTime(open_periods, date, is_open))

        dentists.append(nhs_entity)

    return dentists


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
