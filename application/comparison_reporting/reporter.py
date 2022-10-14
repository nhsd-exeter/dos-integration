import csv
from io import StringIO
from os import makedirs, path
from typing import List

import requests
from aws_lambda_powertools.logging import Logger
from pandas import DataFrame

from common.dos import DoSService, get_all_valid_dos_postcodes
from common.nhs import match_nhs_entities_to_services, NHSEntity
from common.opening_times import SpecifiedOpeningTime
from common.tests.conftest import blank_dos_service

logger = Logger(child=True)


def download_csv_as_dicts(url: str, delimiter: str = ",") -> List[dict]:
    """Takes a url of a csv to download from the web and then returns it as a list of dictionaries."""
    logger.info(f"Attempting to download file: {url}")
    resp = requests.get(url)
    resp.encoding = "ISO-8859-1"
    return [
        {k: v if v != "" else None for k, v in row.items()}
        for row in csv.DictReader(StringIO(resp.text), skipinitialspace=True, delimiter=delimiter)
    ]


class Reporter:
    def __init__(self, nhs_entities: List[NHSEntity], dos_services: List[DoSService], lookup_postcodes: bool = True):
        self.nhs_entities = nhs_entities
        self.dos_services = dos_services
        self.entity_service_map = match_nhs_entities_to_services(self.nhs_entities, self.dos_services)
        self.valid_normalised_postcodes = None
        self.lookup_postcodes = lookup_postcodes

    def run_and_save_reports(self, file_prefix: str, output_dir: str) -> None:
        reports = (
            (self.create_postcode_comparison_report(), "postcode_comparison_report"),
            (self.create_postcode_comparison_report(), "postcode_comparison_report"),
            (self.create_std_opening_times_comparison_report(), "std_opening_times_comparison_report"),
            (self.create_spec_opening_times_comparison_report(), "spec_opening_times_comparison_report"),
            (self.create_invalid_postcode_report(), "invalid_postcode_report"),
            (self.create_invalid_spec_opening_times_report(), "invalid_spec_opening_times_report"),
            (self.create_invalid_std_opening_times_report(), "invalid_std_opening_times_report"),
        )
        if not path.exists(output_dir):
            makedirs(output_dir)
        for report, report_name in reports:
            filename = f"{file_prefix}_{report_name}.csv"
            report.to_csv(path.join(output_dir, filename), index=False)

    def create_postcode_comparison_report(self) -> DataFrame:
        logger.info("Running postcode comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Name",
            "NHSUK Postcode",
            "DoS Service ODSCode",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Service Postcode",
            "DoS Service Status",
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            services = self.entity_service_map.get(nhs_entity.odscode, [])
            for service in services:
                if service.normal_postcode() != nhs_entity.normal_postcode():
                    rows.append(
                        [
                            nhs_entity.odscode,
                            nhs_entity.org_name,
                            nhs_entity.postcode,
                            service.odscode,
                            service.uid,
                            service.name,
                            service.postcode,
                            service.statusid,
                        ]
                    )

        return DataFrame(data=rows, columns=headers)

    def create_std_opening_times_comparison_report(self) -> DataFrame:
        logger.info("Running standard opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Standard Opening Times",
            "DoS Service ODSCode",
            "DoS Service UID",
            "DoS Standard Opening Times",
            "DoS Service Name",
            "DoS Service Status",
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            services = self.entity_service_map.get(nhs_entity.odscode, [])
            for service in services:
                if nhs_entity.standard_opening_times != service.standard_opening_times:
                    rows.append(
                        [
                            nhs_entity.odscode,
                            nhs_entity.standard_opening_times.to_string("\n"),
                            service.odscode,
                            service.uid,
                            service.standard_opening_times.to_string("\n"),
                            service.name,
                            service.statusid,
                        ]
                    )

        return DataFrame(data=rows, columns=headers)

    def create_spec_opening_times_comparison_report(self) -> DataFrame:
        logger.info("Running specified opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Specified Opening Times",
            "DoS Service ODSCode",
            "DoS Service UID",
            "DoS Specified Opening Times",
            "DoS Service Name",
            "DoS Service Status",
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            services = self.entity_service_map.get(nhs_entity.odscode, [])
            for service in services:
                if not SpecifiedOpeningTime.equal_lists(
                        nhs_entity.specified_opening_times,
                        service.specified_opening_times):
                    rows.append(
                        [
                            nhs_entity.odscode,
                            "\n".join(str(spec_open_time) for spec_open_time in nhs_entity.specified_opening_times),
                            service.odscode,
                            service.uid,
                            "\n".join(str(spec_open_time) for spec_open_time in service.specified_opening_times),
                            service.name,
                            service.statusid,
                        ]
                    )

        return DataFrame(data=rows, columns=headers)

    def create_invalid_spec_opening_times_report(self) -> DataFrame:
        logger.info("Running invalid specified opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Specified Opening Times",
            "DoS Service ID",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Service Status",
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            if not SpecifiedOpeningTime.valid_list(nhs_entity.specified_opening_times):
                dos_services = self.entity_service_map.get(nhs_entity.odscode)
                if dos_services is None:
                    dos_services = [blank_dos_service()]
                for dos_service in dos_services:
                    rows.append(
                        [
                            nhs_entity.odscode,
                            nhs_entity.org_name,
                            "\n".join(str(sot) for sot in nhs_entity.specified_opening_times),
                            dos_service.id,
                            dos_service.uid,
                            dos_service.name,
                            dos_service.statusid,
                        ]
                    )

        return DataFrame(data=rows, columns=headers)

    def create_invalid_std_opening_times_report(self) -> DataFrame:
        logger.info("Running invalid standard opening times comparison report.")
        headers = [
            "NHSUK ODSCode",
            "NHSUK Org Name",
            "NHSUK Standard Opening Times",
            "DoS Service ID",
            "DoS Service UID",
            "DoS Service Name",
            "DoS Service Status",
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            if not nhs_entity.standard_opening_times.is_valid():
                dos_services = self.entity_service_map.get(nhs_entity.odscode)
                if dos_services is None:
                    dos_services = [blank_dos_service()]
                for dos_service in dos_services:
                    rows.append(
                        [
                            nhs_entity.odscode,
                            nhs_entity.org_name,
                            nhs_entity.standard_opening_times.to_string("\n"),
                            dos_service.id,
                            dos_service.uid,
                            dos_service.name,
                            dos_service.statusid,
                        ]
                    )

        return DataFrame(data=rows, columns=headers)

    def create_invalid_postcode_report(self) -> DataFrame:
        logger.info("Running Invalid Postcode report.")

        if self.valid_normalised_postcodes is None and self.lookup_postcodes:
            self.valid_normalised_postcodes = get_all_valid_dos_postcodes()

        headers = [
            "NHSUK ODSCode",
            "NHSUK Organisation Name",
            "NHSUK Invalid Postcode",
            "DoS Service ID",
            "DoS Service UID",
            "DoS Service Postcode",
            "DoS Service Status",
        ]
        rows = []
        for nhs_entity in self.nhs_entities:
            if nhs_entity.normal_postcode() not in self.valid_normalised_postcodes:
                dos_services = self.entity_service_map.get(nhs_entity.odscode)
                if dos_services is None:
                    dos_services = [blank_dos_service()]
                for dos_service in dos_services:
                    rows.append(
                        [
                            nhs_entity.odscode,
                            nhs_entity.org_name,
                            nhs_entity.postcode,
                            dos_service.id,
                            dos_service.uid,
                            dos_service.postcode,
                            dos_service.statusid,
                        ]
                    )

        return DataFrame(data=rows, columns=headers)
