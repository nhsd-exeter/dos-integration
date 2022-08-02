from dataclasses import dataclass
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger

from common.constants import (
    DOS_DEMOGRAPHICS_CHANGE_TYPE,
    DOS_DEMOGRAPHICS_CHANGE_TYPE_LIST,
    DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY,
    DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST,
)

logger = Logger(child=True)


@dataclass(repr=True)
class ServiceHistoriesChange:
    """A change to be added to the servicehistories table"""

    data: str
    previous_value: Any
    change_key: str
    change_action: str
    area: str

    def __init__(self, data: Any, previous_value: Any, change_key: str) -> None:
        self.data = data
        self.previous_value = previous_value
        self.change_key = change_key
        self.area = DOS_DEMOGRAPHICS_CHANGE_TYPE
        if self.change_key in DOS_DEMOGRAPHICS_CHANGE_TYPE_LIST:
            self.change_action = self.get_demographics_change_action()
        elif (
            self.change_key in DOS_STANDARD_OPENING_TIMES_CHANGE_KEY_LIST
            or self.change_key == DOS_SPECIFIED_OPENING_TIMES_CHANGE_KEY
        ):
            self.change_action = self.get_opening_times_change_action()
        else:
            logger.error(f"Unknown change key {self.change_key}")
            raise ValueError("Unknown change key")

    def get_demographics_change_action(self) -> str:
        """Gets the change action for a demographics change

        Returns:
            str: Change action - add, remove, modify
        """
        new_value = self.data
        previous_value = self.previous_value
        if previous_value == new_value:
            logger.error(f"previous_value {previous_value} is equal to new_value {new_value}")
            raise ValueError("Previous and new values are the same")
        elif previous_value is None and new_value is not None:
            return "add"
        elif previous_value is not None and new_value is None:
            return "remove"
        else:
            return "modify"

    def get_opening_times_change_action(self) -> str:
        """Gets the change action for a opening times (specified or standard) change

        Returns:
            str: Change action - add, remove, modify
        """
        if "remove" in self.data and "add" in self.data:
            return "modify"
        elif "remove" in self.data:
            return "remove"
        elif "add" in self.data:
            return "add"
        else:
            logger.error(f"Unknown change action from {self.data}")
            raise ValueError("Unknown change action")

    def get_change(self) -> Dict[str, Any]:
        """Gets the change to be added to the servicehistories table

        Returns:
            Dict[str, Any]: Change to be added to the servicehistories table
        """
        return {
            "changetype": self.change_action,
            "data": self.data,
            "area": self.area,
            "previous": self.previous_value,
        }
