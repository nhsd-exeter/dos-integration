from typing import Any

from aws_lambda_powertools.logging import Logger

from ..reporting import log_blank_standard_opening_times
from .changes_to_dos import ChangesToDoS
from .comparison import (
    compare_blood_pressure,
    compare_contraception,
    compare_location,
    compare_palliative_care,
    compare_public_phone,
    compare_specified_opening_times,
    compare_standard_opening_times,
    compare_website,
)
from .service_histories import ServiceHistories
from .service_histories_change import ServiceHistoriesChange
from .validation import validate_opening_times
from common.constants import (
    DI_LATITUDE_CHANGE_KEY,
    DI_LONGITUDE_CHANGE_KEY,
    DOS_ACTIVE_STATUS_ID,
    DOS_ADDRESS_CHANGE_KEY,
    DOS_BLOOD_PRESSURE_TYPE_ID,
    DOS_CLOSED_STATUS_ID,
    DOS_CONTRACEPTION_TYPE_ID,
    DOS_EASTING_CHANGE_KEY,
    DOS_NORTHING_CHANGE_KEY,
    DOS_PALLIATIVE_CARE_SGSDID,
    DOS_PALLIATIVE_CARE_TYPE_ID,
    DOS_POSTAL_TOWN_CHANGE_KEY,
    DOS_POSTCODE_CHANGE_KEY,
    DOS_PUBLIC_PHONE_CHANGE_KEY,
    DOS_SERVICE_HISTORY_ACTIVE_STATUS,
    DOS_SERVICE_HISTORY_CLOSED_STATUS,
    DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST,
    DOS_STATUS_CHANGE_KEY,
    DOS_WEBSITE_CHANGE_KEY,
    MAIN_PHARMACY_ODSCODE_LENGTH,
    NHS_UK_PALLIATIVE_CARE_SERVICE_CODE,
)
from common.dos import DoSService
from common.dos_location import DoSLocation
from common.nhs import NHSEntity, get_palliative_care_log_value, skip_if_key_is_none
from common.opening_times import DAY_IDS, WEEKDAYS

logger = Logger(child=True)


def compare_nhs_uk_and_dos_data(
    dos_service: DoSService,
    nhs_entity: NHSEntity,
    service_histories: ServiceHistories,
) -> ChangesToDoS:
    """Compares the data of the dos_service and nhs_entity and returns a ChangesToDoS object.

    Args:
        dos_service (DoSService): DoSService object to compare
        nhs_entity (NHSEntity): NHS UK entity to compare
        service_histories (ServiceHistories): ServiceHistories object with the service histories of the new changes

    Returns:
        ChangesToDoS: ChangesToDoS class with all the flags if changes need to be made and the changes to make
    """
    # Set up the holder class
    changes_to_dos = ChangesToDoS(dos_service=dos_service, nhs_entity=nhs_entity, service_histories=service_histories)

    # Compare and validate website
    changes_to_dos = check_website_for_change(changes_to_dos=changes_to_dos)
    # Compare public phone
    changes_to_dos = check_public_phone_for_change(changes_to_dos=changes_to_dos)
    #  Compare and validate address & postcode (easting, northing, town, latitude, longitude)
    changes_to_dos = check_location_for_change(changes_to_dos=changes_to_dos)
    # Compare and validate all opening_times
    changes_to_dos = check_opening_times_for_changes(changes_to_dos=changes_to_dos)
    # Compare palliative care
    changes_to_dos = check_palliative_care_for_change(changes_to_dos=changes_to_dos)
    # Compare blood pressure
    changes_to_dos = check_blood_pressure_for_change(changes_to_dos=changes_to_dos)
    # Compare contraception
    return check_contraception_for_change(changes_to_dos=changes_to_dos)


def check_website_for_change(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for website if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if compare_website(changes=changes_to_dos):
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_WEBSITE_CHANGE_KEY,
            new_value=changes_to_dos.new_website,
            previous_value=changes_to_dos.current_website,
            service_table_field_name="web",
        )
    return changes_to_dos


def check_public_phone_for_change(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for public phone if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if compare_public_phone(changes=changes_to_dos):
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_PUBLIC_PHONE_CHANGE_KEY,
            new_value=changes_to_dos.new_public_phone,
            previous_value=changes_to_dos.current_public_phone,
            service_table_field_name="publicphone",
        )
    return changes_to_dos


def check_location_for_change(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates changes individually for location data items if needed.

    Location data covers the following fields:
        - address
        - postcode
        - latitude
        - longitude
        - town
        - easting
        - northing.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    address_change, postcode_change, dos_location = compare_location(changes=changes_to_dos)
    if address_change:
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_ADDRESS_CHANGE_KEY,
            new_value=changes_to_dos.new_address,
            previous_value=changes_to_dos.current_address,
            service_table_field_name="address",
        )
    if postcode_change:
        dos_location: DoSLocation  # dos_location can not be none if postcode must be changed
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_POSTCODE_CHANGE_KEY,
            new_value=changes_to_dos.new_postcode,
            previous_value=changes_to_dos.current_postcode,
            service_table_field_name="postcode",
        )
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_POSTAL_TOWN_CHANGE_KEY,
            new_value=dos_location.postaltown,
            previous_value=changes_to_dos.dos_service.town,
            service_table_field_name="town",
        )
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_EASTING_CHANGE_KEY,
            new_value=dos_location.easting,
            previous_value=changes_to_dos.dos_service.easting,
            service_table_field_name="easting",
        )
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DOS_NORTHING_CHANGE_KEY,
            new_value=dos_location.northing,
            previous_value=changes_to_dos.dos_service.northing,
            service_table_field_name="northing",
        )
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DI_LATITUDE_CHANGE_KEY,
            new_value=dos_location.latitude,
            previous_value=changes_to_dos.dos_service.latitude,
            service_table_field_name="latitude",
            update_service_history=False,
        )
        changes_to_dos = services_change(
            changes_to_dos=changes_to_dos,
            change_key=DI_LONGITUDE_CHANGE_KEY,
            new_value=dos_location.longitude,
            previous_value=changes_to_dos.dos_service.longitude,
            service_table_field_name="longitude",
            update_service_history=False,
        )
    return changes_to_dos


def check_opening_times_for_changes(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates changes individually for all opening times if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if validate_opening_times(dos_service=changes_to_dos.dos_service, nhs_entity=changes_to_dos.nhs_entity):
        logger.debug("Opening times are valid")
        if changes_to_dos.nhs_entity.standard_opening_times.fully_closed():
            log_blank_standard_opening_times(
                nhs_entity=changes_to_dos.nhs_entity,
                dos_service=changes_to_dos.dos_service,
            )
        else:
            logger.warning("Standard opening times are not blank")
            # Compare standard opening times
            for weekday, dos_weekday_key, day_id in zip(  # noqa: B905
                WEEKDAYS,
                DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST,
                DAY_IDS,
            ):
                if compare_standard_opening_times(changes=changes_to_dos, weekday=weekday):
                    changes_to_dos.standard_opening_times_changes[day_id] = getattr(
                        changes_to_dos,
                        f"new_{weekday}_opening_times",
                    )
                    changes_to_dos.service_histories.add_standard_opening_times_change(
                        current_opening_times=changes_to_dos.dos_service.standard_opening_times,
                        new_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
                        dos_weekday_change_key=dos_weekday_key,
                        weekday=weekday,
                    )

        if compare_specified_opening_times(changes=changes_to_dos):
            changes_to_dos.specified_opening_times_changes = True
            changes_to_dos.service_histories.add_specified_opening_times_change(
                current_opening_times=changes_to_dos.current_specified_opening_times,
                new_opening_times=changes_to_dos.new_specified_opening_times,
            )
    else:
        logger.info(
            "Opening times are not valid",
            nhs_uk_standard_opening_times=changes_to_dos.nhs_entity.standard_opening_times,
            nhs_uk_specified_opening_times=changes_to_dos.nhs_entity.specified_opening_times,
        )
    return changes_to_dos


def check_palliative_care_for_change(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for palliative care if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    skip_palliative_care_check = skip_if_key_is_none(
        changes_to_dos.nhs_entity.check_for_uec_service(NHS_UK_PALLIATIVE_CARE_SERVICE_CODE),
    )
    if (
        changes_to_dos.dos_service.typeid == DOS_PALLIATIVE_CARE_TYPE_ID
        and len(changes_to_dos.dos_service.odscode) == MAIN_PHARMACY_ODSCODE_LENGTH
        and compare_palliative_care(changes=changes_to_dos)
        and skip_palliative_care_check is False
    ):
        changes_to_dos.palliative_care_changes = True

        changes_to_dos.service_histories.add_sgsdid_change(
            sgsdid=DOS_PALLIATIVE_CARE_SGSDID,
            new_value=changes_to_dos.nhs_entity.palliative_care,
        )
    else:
        logger.info(
            "No change / Not suitable for palliative care comparison",
            nhs_uk_palliative_care=get_palliative_care_log_value(
                changes_to_dos.nhs_entity.palliative_care,
                skip_palliative_care_check,
            ),
            dos_palliative_care=changes_to_dos.dos_service.palliative_care,
            dos_odscode=changes_to_dos.dos_service.odscode,
            skip_palliative_care_check=skip_palliative_care_check,
        )
    return changes_to_dos


def check_blood_pressure_for_change(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for blood pressure if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if changes_to_dos.dos_service.typeid != DOS_BLOOD_PRESSURE_TYPE_ID:
        logger.info("Not Suitable for blood pressure comparison", dos_service_type_id=changes_to_dos.dos_service.typeid)
        return changes_to_dos

    if compare_blood_pressure(changes=changes_to_dos):
        changes_to_dos.blood_pressure_changes = True
        status_id_change(
            changes_to_dos=changes_to_dos,
            new_value=changes_to_dos.nhs_entity.blood_pressure,
            previous_value=changes_to_dos.dos_service.status_name,
        )
    else:
        logger.info(
            "No change to blood pressure",
            dos_service_type_id=changes_to_dos.dos_service.typeid,
            nhs_uk_blood_pressure=changes_to_dos.nhs_entity.blood_pressure,
            dos_blood_pressure=changes_to_dos.dos_service.status_name,
        )

    return changes_to_dos


def check_contraception_for_change(changes_to_dos: ChangesToDoS) -> ChangesToDoS:
    """Compares and creates change for contraception if needed.

    Args:
        changes_to_dos (ChangesToDoS): ChangesToDoS holder object

    Returns:
        ChangesToDoS: ChangesToDoS holder object
    """
    if changes_to_dos.dos_service.typeid != DOS_CONTRACEPTION_TYPE_ID:
        logger.info("Not Suitable for contraception comparison", dos_service_type_id=changes_to_dos.dos_service.typeid)
        return changes_to_dos

    if compare_contraception(changes=changes_to_dos):
        changes_to_dos.contraception_changes = True
        status_id_change(
            changes_to_dos=changes_to_dos,
            new_value=changes_to_dos.nhs_entity.contraception,
            previous_value=changes_to_dos.dos_service.status_name,
        )
    else:
        logger.info(
            "No change to contraception",
            dos_service_type_id=changes_to_dos.dos_service.typeid,
            nhs_uk_contraception=changes_to_dos.nhs_entity.contraception,
            dos_contraception=changes_to_dos.dos_service.status_name,
        )

    return changes_to_dos


def services_change(
    changes_to_dos: ChangesToDoS,
    change_key: str,
    new_value: Any,  # noqa: ANN401
    previous_value: Any,  # noqa: ANN401
    service_table_field_name: str,
    update_service_history: bool = True,
) -> ChangesToDoS:
    """Runs the prerequisites for a change to the services table.

    Including adding the change to the change object, and updating the service history.

    Args:
        changes_to_dos (ChangesToDoS): The changes to dos object
        change_key (str): The service history change key
        new_value (Any): The new value to set the service table field to
        previous_value (Any): The previous value of the service table field
        service_table_field_name (str): The name of the service table field to set
        update_service_history (bool): Whether to update the service history. Defaults to True.

    Returns:
        ChangesToDoS: The changes to dos object
    """
    changes_to_dos.demographic_changes[service_table_field_name] = str(new_value) if new_value is not None else ""
    if update_service_history:
        changes_to_dos.service_histories.add_change(
            dos_change_key=change_key,
            change=ServiceHistoriesChange(
                data=new_value,
                previous_value=previous_value,
                change_key=change_key,
            ),
        )
    return changes_to_dos


def status_id_change(changes_to_dos: ChangesToDoS, new_value: bool, previous_value: str) -> ChangesToDoS:
    """Runs the prerequisites for a change to the services table.

    Including adding the change to the change object, and updating the service history.

    Args:
        changes_to_dos (ChangesToDoS): The changes to dos object
        new_value (int): The new value to set the service table field to
        previous_value (str): The previous value of the service table field

    Returns:
        ChangesToDoS: The changes to dos object
    """
    status_id, status_name = (
        DOS_ACTIVE_STATUS_ID if new_value else DOS_CLOSED_STATUS_ID,
        DOS_SERVICE_HISTORY_ACTIVE_STATUS if new_value else DOS_SERVICE_HISTORY_CLOSED_STATUS,
    )
    changes_to_dos.demographic_changes["statusid"] = status_id
    changes_to_dos.service_histories.add_change(
        dos_change_key=DOS_STATUS_CHANGE_KEY,
        change=ServiceHistoriesChange(
            data=status_name,
            previous_value=previous_value,
            change_key=DOS_STATUS_CHANGE_KEY,
        ),
    )
    return changes_to_dos
