from os import path
import io
from typing import List
import csv
from collections import defaultdict
from pandas import DataFrame
import pathlib
import requests

from aws_lambda_powertools import Logger

from common.nhs import NHSEntity
from common.dos import DoSService, get_all_valid_dos_postcodes
from common.opening_times import OpenPeriod, SpecifiedOpeningTime, WEEKDAYS

logger = Logger(child=True)
THIS_DIR = pathlib.Path(__file__).parent.resolve()
OUTPUT_DIR = path.join(THIS_DIR, "out")


def download_csv_as_dicts(url: str, delimiter: str = ",") -> List[dict]:
    """Takes a url of a csv to download from the web and then returns it as a list of dictionaries."""
    resp = requests.get(url)
    csv_file_like_obj = io.StringIO(resp.text)
    return [{k: v if v != "" else None for k, v in row.items()}
            for row in csv.DictReader(csv_file_like_obj, skipinitialspace=True, delimiter=delimiter)]


def match_nhs_entities_to_services(nhs_entities: List[NHSEntity], services: List[DoSService]):
    logger.info("Matching all NHS Entities to corresponding list of services.")
    servicelist_map = defaultdict(list)
    for nhs_entity in nhs_entities:
        for service in services:
            if nhs_entity.is_matching_dos_service(service):
                servicelist_map[nhs_entity.odscode].append(service)

    logger.info(
        f"{len(servicelist_map)}/{len(nhs_entities)} nhs entities matches with at least 1 service. "
        f"{len(nhs_entities) - len(servicelist_map)} not matched."
    )
    return servicelist_map


class Reporter:

    def __init__(self, nhs_entities: List[NHSEntity], dos_services: List[DoSService]):
        self.nhs_entities = nhs_entities
        self.dos_services = dos_services
        self.entity_service_map = match_nhs_entities_to_services(self.nhs_entities, self.dos_services)
        self.valid_normalised_postcodes = None

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

    def create_invalid_spec_opening_times_report(self, filename: str):
        logger.info("Running invalid specified opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Specified Opening Times"
        ]
        rows = []
        for nhs_entity in self.nhs_entities:

            if not SpecifiedOpeningTime.valid_list(nhs_entity.specified_opening_times):
                rows.append([
                    nhs_entity.odscode,
                    nhs_entity.org_name,
                    "\n".join(str(sot) for sot in nhs_entity.specified_opening_times)
                ])

        df = DataFrame(data=rows, columns=headers)
        pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)
        df.to_csv(path.join(OUTPUT_DIR, filename), index=False)

    def create_invalid_std_opening_times_report(self, filename: str):
        logger.info("Running invalid standard opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Standard Opening Times"
        ]
        rows = []
        for nhs_entity in self.nhs_entities:

            if not nhs_entity.standard_opening_times.is_valid():
                rows.append([
                    nhs_entity.odscode,
                    nhs_entity.org_name,
                    "\n".join([f"{day}={OpenPeriod.list_string(getattr(nhs_entity.standard_opening_times, day))}"
                            for day in WEEKDAYS])
                ])

        df = DataFrame(data=rows, columns=headers)
        pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)
        df.to_csv(path.join(OUTPUT_DIR, filename), index=False)

    def create_invalid_postcode_report(self, filename: str):
        logger.info("Running Invalid Postcode report.")

        if self.valid_normalised_postcodes is None:
            self.valid_normalised_postcodes = get_all_valid_dos_postcodes()

        headers = [
            "NHSUK ODSCode",
            "NHSUK Organisation Name",
            "NHSUK Invalid Postcode"
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            if nhs_entity.normal_postcode() not in self.valid_normalised_postcodes:
                rows.append([
                    nhs_entity.odscode,
                    nhs_entity.org_name,
                    nhs_entity.postcode
                ])

        df = DataFrame(data=rows, columns=headers)
        pathlib.Path(OUTPUT_DIR).mkdir(exist_ok=True)
        df.to_csv(path.join(OUTPUT_DIR, filename), index=False)
