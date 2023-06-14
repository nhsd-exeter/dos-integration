from os import environ
from typing import Any

from aws_embedded_metrics import metric_scope
from aws_lambda_powertools.logging.logger import Logger

from common.dos import DoSService
from common.nhs import NHSEntity
from common.opening_times import OpenPeriod

logger = Logger(child=True)

BLANK_STANDARD_OPENINGS_REPORT_ID = "BLANK_STANDARD_OPENINGS"
GENERIC_BANK_HOLIDAY_REPORT_ID = "GENERIC_BANK_HOLIDAY"
GENERIC_CHANGE_EVENT_ERROR_REPORT_ID = "GENERIC_CHANGE_EVENT_ERROR"
INCORRECT_PALLIATIVE_STOCKHOLDER_TYPE_REPORT_ID = "INCORRECT_PALLIATIVE_STOCKHOLDER_TYPE"
INVALID_POSTCODE_REPORT_ID = "INVALID_POSTCODE"
SERVICE_UPDATE_REPORT_ID = "SERVICE_UPDATE"


def log_blank_standard_opening_times(
    nhs_entity: NHSEntity,
    dos_service: DoSService,
) -> None:
    """Log events where matches services are found but no std opening times exist.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        dos_service (DoSService): The list of DoS matching services
    """
    logger.warning(
        "NHS Service has matching DoS services but no given standard opening times.",
        extra={
            "report_key": BLANK_STANDARD_OPENINGS_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "dos_service_id": dos_service.id,
            "dos_service_uid": dos_service.uid,
            "dos_service_name": dos_service.name,
            "nhsuk_service_status": nhs_entity.org_status,
            "nhsuk_service_type": nhs_entity.org_type,
            "nhsuk_sector": nhs_entity.org_sub_type,
            "dos_service_status": dos_service.statusid,
            "dos_service_type": dos_service.typeid,
            "dos_service_type_name": dos_service.servicename,
            "dos_region": dos_service.get_region(),
        },
    )


@metric_scope
def log_invalid_nhsuk_postcode(
    nhs_entity: NHSEntity,
    dos_service: DoSService,
    metrics: Any,  # noqa: ANN401
) -> None:
    """Log invalid NHS pharmacy postcode.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        dos_service (List[DoSService]): The list of DoS matching services.
        metrics (Any): The metrics object to report to.
    """
    error_msg = f"NHS entity '{nhs_entity.odscode}' postcode '{nhs_entity.postcode}' is not a valid DoS postcode!"
    logger.warning(
        error_msg,
        extra={
            "report_key": INVALID_POSTCODE_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "nhsuk_organisation_type": nhs_entity.org_type,
            "nhsuk_organisation_subtype": nhs_entity.org_sub_type,
            "nhsuk_address1": nhs_entity.entity_data.get("Address1", ""),
            "nhsuk_address2": nhs_entity.entity_data.get("Address2", ""),
            "nhsuk_address3": nhs_entity.entity_data.get("Address3", ""),
            "nhsuk_city": nhs_entity.entity_data.get("City", ""),
            "nhsuk_county": nhs_entity.entity_data.get("County", ""),
            "nhsuk_postcode": nhs_entity.postcode,
            "validation_error_reason": "Postcode not valid/found on DoS",
            "dos_service": dos_service.uid,
            "dos_service_type_name": dos_service.servicename,
        },
    )
    metrics.set_namespace("UEC-DOS-INT")
    metrics.set_property("level", "WARNING")
    metrics.set_property("message", error_msg)
    metrics.set_property("correlation_id", logger.get_correlation_id())
    metrics.set_property("ods_code", nhs_entity.odscode)
    metrics.set_dimensions({"ENV": environ["ENV"]})
    metrics.put_metric("InvalidPostcode", 1, "Count")


def log_service_with_generic_bank_holiday(
    nhs_entity: NHSEntity,
    dos_service: DoSService,
) -> None:
    """Log a service found to have a generic bank holiday open times set in DoS.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        dos_service (DoSService): The DoS service to report
    """
    open_periods_str = OpenPeriod.list_string(
        dos_service.standard_opening_times.generic_bankholiday,
    )

    logger.warning(
        f"DoS Service uid={dos_service.uid} has a generic BankHoliday Standard opening time set in DoS",
        extra={
            "report_key": GENERIC_BANK_HOLIDAY_REPORT_ID,
            "nhsuk_odscode": nhs_entity.odscode,
            "nhsuk_organisation_name": nhs_entity.org_name,
            "dos_service_uid": dos_service.uid,
            "dos_service_name": dos_service.name,
            "dos_service_type_id": dos_service.typeid,
            "bank_holiday_opening_times": open_periods_str,
            "nhsuk_parentorg": nhs_entity.parent_org_name,
            "dos_service_type_name": dos_service.servicename,
        },
    )


def log_website_is_invalid(nhs_uk_entity: NHSEntity, nhs_website: str) -> None:
    """Log a service found to have an invalid website.

    Args:
        nhs_uk_entity (NHSEntity): The NHS entity to report
        nhs_website (str): The NHS website to report
    """
    logger.warning(
        f"Website is not valid, {nhs_website=}",
        extra={
            "report_key": GENERIC_CHANGE_EVENT_ERROR_REPORT_ID,
            "error_reason": "Website is not valid",
            "error_info": f"NHSUK unedited website: '{nhs_uk_entity.website}', NHSUK website='{nhs_website}'",
            "nhs_unedited_website": nhs_uk_entity.website,
            "nhs_website": nhs_website,
        },
    )


def log_palliative_care_z_code_does_not_exist(
    symptom_group_symptom_discriminator_combo_rowcount: int,
) -> None:
    """Log a service found to have an invalid website.

    Args:
        symptom_group_symptom_discriminator_combo_rowcount (int): The number of rows returned from the database query
    """
    logger.warning(
        "Palliative care Z code does not exist in the DoS database",
        extra={
            "report_key": GENERIC_CHANGE_EVENT_ERROR_REPORT_ID,
            "error_reason": "Palliative care Z code does not exist",
            "error_info": (
                f"symptom_group_symptom_discriminator={bool(symptom_group_symptom_discriminator_combo_rowcount)}"
            ),
        },
    )


def log_service_updated(  # noqa: PLR0913
    action: str,
    data_field_modified: str,
    new_value: str,
    previous_value: str,
    service_name: str,
    service_uid: str,
    type_id: str,
) -> None:
    """Log a service update.

    Args:
        action (str): The action performed
        data_field_modified (str): The data field modified
        new_value (str): The new value
        previous_value (str): The previous value
        service_name (str): The service name
        service_uid (str): The service uid
        type_id (str): The type id
    """
    logger.warning(
        "Service update complete",
        extra={
            "report_key": SERVICE_UPDATE_REPORT_ID,
            "action": action,
            "previous_value": previous_value,
            "new_value": new_value,
            "data_field_modified": data_field_modified,
            "service_name": service_name,
            "service_uid": service_uid,
            "type_id": type_id,
        },
    )


def log_incorrect_palliative_stockholder_type(
    nhs_uk_palliative_care: bool | str,
    dos_palliative_care: bool,
    dos_service: DoSService,
) -> None:
    """Log a service found to have an invalid website.

    Args:
        nhs_uk_palliative_care (bool): The NHS website to report
        dos_palliative_care (bool): The NHS entity to report
        dos_service (DoSService): The DoS service to report
    """
    logger.warning(
        "Palliative care on wrong service type",
        extra={
            "report_key": INCORRECT_PALLIATIVE_STOCKHOLDER_TYPE_REPORT_ID,
            "dos_palliative_care": dos_palliative_care,
            "nhsuk_palliative_care": nhs_uk_palliative_care,
            "dos_service_type_name": dos_service.servicename,
        },
    )
