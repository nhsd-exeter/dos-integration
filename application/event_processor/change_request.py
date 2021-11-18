from os import environ


class ChangeRequest:
    def __init__(self, service_id, changes) -> None:
        trace_id = environ.get("_X_AMZN_TRACE_ID", default="<NO-TRACE-ID>")
        self.change_request = {
            "reference": str(trace_id),
            "system": "DoS Integration",
            "message": f"DoS Integration CR. AMZN-trace-id: {trace_id}",
            "service_id": str(service_id),
            "changes": changes,
        }

    def get_change_request(self) -> dict:
        return self.change_request
