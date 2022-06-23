from typing import Any, Dict
from aws_lambda_powertools import Logger


ADDRESS_CHANGE_KEY = "address"
ADDRESS_LINES_KEY = "address_lines"
PHONE_CHANGE_KEY = "phone"
POSTCODE_CHANGE_KEY = "post_code"
WEBSITE_CHANGE_KEY = "website"
OPENING_DATES_KEY = "opening_dates"
OPENING_DAYS_KEY = "opening_days"


logger = Logger(child=True)


class ChangeRequest:
    changes: Dict[str, Any]

    def __init__(self, service_id: int, changes: Any = None):
        correlation_id = logger.get_correlation_id()

        self.reference = correlation_id
        self.system = "DoS Integration"
        self.message = f"DoS Integration CR. correlation-id: {correlation_id}"
        self.replace_opening_dates_mode = True
        self.service_id = str(service_id)
        self.changes = changes
        if self.changes is None:
            self.changes = {}

    def create_payload(self) -> Dict[str, Any]:
        """Creates the payload for the change request

        Returns:
            Dict[str, Any]: The change request payload
        """
        return {
            "reference": self.reference,
            "system": self.system,
            "message": self.message,
            "replace_opening_dates_mode": self.replace_opening_dates_mode,
            "service_id": self.service_id,
            "changes": self.changes,
        }
