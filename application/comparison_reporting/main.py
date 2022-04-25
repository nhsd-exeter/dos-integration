from os import path
from itertools import groupby
from typing import List
import csv
from pprint import pprint as pp
from collections import defaultdict
from datetime import datetime
from pandas import DataFrame
import pathlib

from aws_lambda_powertools import Logger

from common.constants import DENTIST_SERVICE_TYPE_IDS
from common.nhs import NHSEntity
from common.dos import DoSService, get_services_from_db
from common.opening_times import StandardOpeningTimes, OpenPeriod, SpecifiedOpeningTime, WEEKDAYS

logger = Logger(child=True)
THIS_DIR = pathlib.Path(__file__).parent.resolve()
OUTPUT_DIR = path.join(THIS_DIR, "out")


def csv_to_dicts(csv_file, delimiter=",") -> List[dict]:
    with open(csv_file, "r") as f:
        return [{k: v if v != "" else None for k, v in row.items()} 
                for row in csv.DictReader(f, skipinitialspace=True, delimiter=delimiter)]


def get_dentist_data() -> List[dict]:
    return csv_to_dicts("comparison_reporting/Dentists.csv", delimiter="¬")


def get_dentist_open_times_data() -> List[dict]:
    return csv_to_dicts("comparison_reporting/DentistOpeningTimes.csv", delimiter="¬")


def get_dentists() -> List[NHSEntity]:

    dentists_data = get_dentist_data()
    dentists_open_times_data = get_dentist_open_times_data()

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
            logger.warning(f"Unknown opening type f'{opening_type}'.")

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
        for date, open_period_items in groupby(spec_open_data.get(id, []), 
                lambda k: datetime.strptime(k["AdditonalOpeningDate"], "%b  %d  %Y").date()):

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




def match_nhs_entiity_to_services(nhs_entities: List[NHSEntity], services: List[DoSService]):
    logger.info("Matching all NHS Entities to corresponding list of services.")
    servicelist_map = defaultdict(list)
    for nhs_entity in nhs_entities:
        for service in services:
            if service.nhs_odscode_match(nhs_entity.odscode):
                servicelist_map[nhs_entity.odscode].append(service)
    unmatched = len(nhs_entities) - len(servicelist_map)
    logger.info(
        f"{len(servicelist_map)}/{len(nhs_entities)} nhs entities matches with at least 1 service. "
        f"{unmatched} not matched."
    )
    return servicelist_map


def run_dentist_reports():

    nhsuk_dentists = get_dentists()
    dentist_dos_services = get_services_from_db(DENTIST_SERVICE_TYPE_IDS)
    reporter = Reporter(nhs_entities=nhsuk_dentists, dos_services=dentist_dos_services)
    reporter.create_postcode_comparison_report(filename="dentists_postcode_comparison_report.csv")
    reporter.create_std_opening_times_comparison_report(filename="dentists_standard_opening_times_comparison_report.csv")
    reporter.create_spec_opening_times_comparison_report(filename="dentists_specified_opening_times_comparison_report.csv")

class Reporter:

    def __init__(self, nhs_entities: List[NHSEntity], dos_services: List[DoSService]):
        self.nhs_entities = nhs_entities
        self.dos_services = dos_services
        self.entity_service_map = match_nhs_entiity_to_services(self.nhs_entities, self.dos_services)


    def create_postcode_comparison_report(self, filename: str):
        logger.info("Running postcode comparison report.")
        headers = [
            "NHSUK ODSCode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "NHSUK Postcode",
            "DoS Service Postcode"
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            services = self.entity_service_map.get(nhs_entity.odscode, [])
            for service in services:
                if service.normal_postcode() != nhs_entity.normal_postcode():
                    rows.append([
                        nhs_entity.odscode,
                        service.odscode,
                        service.uid,
                        nhs_entity.postcode,
                        service.postcode
                    ])
        
        df = DataFrame(data=rows, columns=headers)
        pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)
        df.to_csv(path.join(OUTPUT_DIR, filename), index=False)


    def create_std_opening_times_comparison_report(self, filename: str):
        logger.info("Running standard opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "NHSUK Standard Opening Times",
            "DoS Standard Opening Times"
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            services = self.entity_service_map.get(nhs_entity.odscode, [])
            for service in services:
                if nhs_entity.standard_opening_times != service._standard_opening_times:
                    rows.append([
                        nhs_entity.odscode,
                        service.odscode,
                        service.uid,
                        "\n".join([f"{day}={OpenPeriod.list_string(getattr(nhs_entity.standard_opening_times, day))}"
                            for day in WEEKDAYS]),
                        "\n".join([f"{day}={OpenPeriod.list_string(getattr(service._standard_opening_times, day))}"
                            for day in WEEKDAYS])
                    ])
        
        df = DataFrame(data=rows, columns=headers)
        pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)
        df.to_csv(path.join(OUTPUT_DIR, filename), index=False)


    def create_spec_opening_times_comparison_report(self, filename: str):
        logger.info("Running specified opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "NHSUK Specified Opening Times",
            "DoS Specified Opening Times"
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            services = self.entity_service_map.get(nhs_entity.odscode, [])
            for service in services:

                if not SpecifiedOpeningTime.equal_lists(
                        nhs_entity.specified_opening_times, 
                        service._specified_opening_times):

                    rows.append([
                        nhs_entity.odscode,
                        service.odscode,
                        service.uid,
                        "\n".join(str(sot) for sot in nhs_entity.specified_opening_times),
                        "\n".join(str(sot) for sot in service._specified_opening_times)
                    ])
        
        df = DataFrame(data=rows, columns=headers)
        pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)
        df.to_csv(path.join(OUTPUT_DIR, filename), index=False)



     
run_dentist_reports()
