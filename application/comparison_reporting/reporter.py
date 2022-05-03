from os import path
from io import StringIO
from typing import List
import csv
from pandas import DataFrame
import pathlib
import requests

from aws_lambda_powertools import Logger

from common.nhs import NHSEntity, match_nhs_entities_to_services
from common.dos import DoSService, get_all_valid_dos_postcodes
from common.opening_times import SpecifiedOpeningTime

logger = Logger(child=True)


def download_csv_as_dicts(url: str, delimiter: str = ",") -> List[dict]:
    """Takes a url of a csv to download from the web and then returns it as a list of dictionaries."""
    resp = requests.get(url)
    return [{k: v if v != "" else None for k, v in row.items()}
            for row in csv.DictReader(StringIO(resp.text), skipinitialspace=True, delimiter=delimiter)]


class Reporter:

    def __init__(self, nhs_entities: List[NHSEntity], dos_services: List[DoSService]):
        self.nhs_entities = nhs_entities
        self.dos_services = dos_services
        self.entity_service_map = match_nhs_entities_to_services(self.nhs_entities, self.dos_services)
        self.valid_normalised_postcodes = None

    def run_and_save_reports(self, file_prefix: str, output_dir: str) -> None:
        reports = (
            (self.create_postcode_comparison_report(), "postcode_comparison_report"),
            (self.create_postcode_comparison_report(), "postcode_comparison_report"),
            (self.create_std_opening_times_comparison_report(), "std_opening_times_comparison_report"),
            (self.create_spec_opening_times_comparison_report(), "spec_opening_times_comparison_report"),
            (self.create_invalid_postcode_report(), "invalid_postcode_report"),
            (self.create_invalid_spec_opening_times_report(), "invalid_spec_opening_times_report"),
            (self.create_invalid_std_opening_times_report(), "invalid_std_opening_times_report")
        )
        pathlib.Path(output_dir).mkdir(exist_ok=True)
        for report, report_name in reports:
            filename = f"{file_prefix}_{report_name}.csv"
            report.to_csv(path.join(output_dir, filename), index=False)

    def create_postcode_comparison_report(self) -> DataFrame:
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

        return DataFrame(data=rows, columns=headers)

    def create_std_opening_times_comparison_report(self) -> DataFrame:
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
                        nhs_entity.standard_opening_times.to_string("\n"),
                        service._standard_opening_times.to_string("\n")
                    ])

        return DataFrame(data=rows, columns=headers)

    def create_spec_opening_times_comparison_report(self) -> DataFrame:
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

        return DataFrame(data=rows, columns=headers)

    def create_invalid_spec_opening_times_report(self) -> DataFrame:
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

        return DataFrame(data=rows, columns=headers)

    def create_invalid_std_opening_times_report(self) -> DataFrame:
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
                    nhs_entity.standard_opening_times.to_string("\n")
                ])

        return DataFrame(data=rows, columns=headers)

    def create_invalid_postcode_report(self) -> DataFrame:
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

        return DataFrame(data=rows, columns=headers)
