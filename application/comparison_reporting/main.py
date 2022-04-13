from asyncio.log import logger
from itertools import groupby
from operator import imod
from typing import List
import csv
from pprint import pprint as pp
from collections import defaultdict
from logging import Logger
from datetime import datetime

from common.constants import DENTIST_ORG_TYPE_ID
from common.nhs import NHSEntity
from common.dos import get_matching_dos_services
from common.opening_times import StandardOpeningTimes, OpenPeriod, SpecifiedOpeningTime

logger = Logger("")


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


def run_report():

    dentists = get_dentists()
    


    for dentist in dentists:
        print(f"Searching for dentist services {dentist}")
        services = get_matching_dos_services(dentist.odscode, DENTIST_ORG_TYPE_ID)
        pp(services)
        print(f"{len(services)} found.")
        if len(services) > 0:
            break


run_report()