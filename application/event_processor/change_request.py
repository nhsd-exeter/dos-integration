from os import environ

ADDRESS_CHANGE_KEY = "address"
PHONE_CHANGE_KEY = "phone"
POSTCODE_CHANGE_KEY = "postcode"
PUBLICNAME_CHANGE_KEY = "publicname"
WEBSITE_CHANGE_KEY = "website"
OPENING_DATES_KEY = "opening_dates"
OPENING_DAYS_KEY = "opening_days"

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"


class ChangeRequest:
    def __init__(self, service_id, changes=[]):
        trace_id = environ.get("_X_AMZN_TRACE_ID", default="<NO-TRACE-ID>")

        self.reference =  str(trace_id)
        self.system = "DoS Integration"
        self.message = f"DoS Integration CR. AMZN-trace-id: {trace_id}"
        self.service_id = str(service_id)
        self.changes = changes

    def get_change_request(self) -> dict:
        return {
            "reference": self.reference,
            "system": self.system,
            "message": self.message,
            "service_id": self.service_id,
            "changes": self.changes
        }
