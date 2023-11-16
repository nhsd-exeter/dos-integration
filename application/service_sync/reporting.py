from os import getenv

from aws_lambda_powertools.logging.logger import Logger

from common.dos import DoSService
from common.nhs import NHSEntity
from common.opening_times import OpenPeriod

logger = Logger(child=True)

BLANK_STANDARD_OPENINGS_REPORT_ID = "BLANK_STANDARD_OPENINGS"
GENERIC_BANK_HOLIDAY_REPORT_ID = "GENERIC_BANK_HOLIDAY"
GENERIC_CHANGE_EVENT_ERROR_REPORT_ID = "GENERIC_CHANGE_EVENT_ERROR"
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
        report_key=BLANK_STANDARD_OPENINGS_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        dos_service_id=dos_service.id,
        dos_service_uid=dos_service.uid,
        dos_service_name=dos_service.name,
        nhsuk_service_status=nhs_entity.org_status,
        nhsuk_service_type=nhs_entity.org_type,
        nhsuk_sector=nhs_entity.org_sub_type,
        dos_service_status=dos_service.statusid,
        dos_service_type=dos_service.typeid,
        dos_service_type_name=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
    )


def log_invalid_nhsuk_postcode(
    nhs_entity: NHSEntity,
    dos_service: DoSService,
) -> None:
    """Log invalid NHS pharmacy postcode.

    Args:
        nhs_entity (NHSEntity): The NHS entity to report
        dos_service (DoSService): DoS service to report
    """
    error_msg = f"NHS entity '{nhs_entity.odscode}' postcode '{nhs_entity.postcode}' is not a valid DoS postcode!"
    logger.warning(
        error_msg,
        report_key=INVALID_POSTCODE_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_type=nhs_entity.org_type,
        nhsuk_organisation_name=nhs_entity.org_name,
        nhsuk_organisation_subtype=nhs_entity.org_sub_type,
        nhsuk_address1=nhs_entity.entity_data.get("Address1", ""),
        nhsuk_address2=nhs_entity.entity_data.get("Address2", ""),
        nhsuk_address3=nhs_entity.entity_data.get("Address3", ""),
        nhsuk_city=nhs_entity.entity_data.get("City", ""),
        nhsuk_county=nhs_entity.entity_data.get("County", ""),
        nhsuk_postcode=nhs_entity.postcode,
        validation_error_reason="Postcode not valid/found on DoS",
        dos_service=dos_service.uid,
        dos_service_type_name=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
        dos_service_name=dos_service.name,
        environment=getenv("ENVIRONMENT"),
        cloudwatch_metric_filter_matching_attribute="InvalidPostcode",
    )


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
        report_key=GENERIC_BANK_HOLIDAY_REPORT_ID,
        nhsuk_odscode=nhs_entity.odscode,
        nhsuk_organisation_name=nhs_entity.org_name,
        dos_service_uid=dos_service.uid,
        dos_service_name=dos_service.name,
        bank_holiday_opening_times=open_periods_str,
        nhsuk_parent_org=nhs_entity.parent_org_name,
        dos_service_type_name=dos_service.service_type_name,
        dos_region=dos_service.get_region(),
    )


def log_website_is_invalid(nhs_uk_entity: NHSEntity, nhs_website: str, dos_service: DoSService) -> None:
    """Log a service found to have an invalid website.

    Args:
        nhs_uk_entity (NHSEntity): The NHS entity to report
        nhs_website (str): The NHS website to report
        dos_service (DoSService): The DoS service to report
    """
    log_generic_change_event_error(
        "Website is not valid",
        "Website is not valid",
        f"NHSUK unedited website: '{nhs_uk_entity.website}', NHSUK website='{nhs_website}'",
        dos_service,
        {
            "nhs_unedited_website": nhs_uk_entity.website,
            "nhs_website": nhs_website,
        },
    )


def log_generic_change_event_error(
    message: str,
    error_reason: str,
    error_info: str,
    dos_service: DoSService,
    extra: dict[str, str] | None = None,
) -> None:
    """Log a generic change event error.

    Args:
        message (str): The message to log
        error_reason (str): The error reason
        error_info (str): The error info
        dos_service (DoSService): The DoS service to report
        extra (dict[str, str], optional): Extra information to log. Defaults to None.
    """
    logger.warning(
        message,
        report_key=GENERIC_CHANGE_EVENT_ERROR_REPORT_ID,
        error_reason=error_reason,
        error_info=error_info,
        dos_region=dos_service.get_region(),
        extra=extra,
    )


def log_service_updated(  # noqa: PLR0913
    action: str,
    data_field_modified: str,
    new_value: str,
    previous_value: str,
    service_name: str,
    service_uid: str,
    type_id: str,
    dos_service: DoSService,
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
        dos_service (DoSService): The DoS service to report
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
            "dos_region": dos_service.get_region(),
            "environment": getenv("ENVIRONMENT"),
            "cloudwatch_metric_filter_matching_attribute": "ServiceUpdate",
        },
    )
