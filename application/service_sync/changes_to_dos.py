from dataclasses import dataclass, field
from typing import Any

from aws_lambda_powertools.logging import Logger

from .service_histories import ServiceHistories
from common.dos import DoSService
from common.nhs import NHSEntity
from common.opening_times import SpecifiedOpeningTime

logger = Logger(child=True)


@dataclass(init=True, repr=True)
class ChangesToDoS:
    """Class to determine if an update needs to be made to the DoS db and if so, what the update should be."""

    # Holding data classes for use within this class
    dos_service: DoSService
    nhs_entity: NHSEntity
    service_histories: ServiceHistories
    # Variable to know if fields need to be changed
    demographic_changes: dict[str | None, Any] = field(default_factory=dict)
    standard_opening_times_changes: dict[int | None, Any] = field(default_factory=dict)
    specified_opening_times_changes: bool = False
    palliative_care_changes: bool = False

    # New value to be saved to the database
    new_address: str | None = None
    new_postcode: str | None = None
    new_public_phone: str | None = None
    new_specified_opening_times: list[SpecifiedOpeningTime] | None = None
    new_website: str | None = None
    new_palliative_care: bool | None = None

    # Existing DoS data for use building service history
    current_address: str | None = None
    current_postcode: str | None = None
    current_public_phone: str | None = None
    current_specified_opening_times: list[SpecifiedOpeningTime] | None = None
    current_website: str | None = None
    current_palliative_care: bool | None = None

    # Each day that has changed will have a current and new value in the format below
    # new_day_opening_times e.g. new_monday_opening_times
    # current_day_opening_times e.g. current_monday_opening_times
    # The type of the value is a list of OpenPeriod objects
