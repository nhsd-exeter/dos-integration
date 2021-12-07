



from opening_times import StandardOpeningTimes
import random
from nhs import NHSEntity
from event_processor import get_changes
from dos import DoSService

def dummy_dos_service() -> DoSService:
    """Creates a DoSService Object with random data for the unit testing"""
    test_data = []
    for col in DoSService.db_columns:
        random_str = "".join(random.choices("ABCDEFGHIJKLM", k=8))
        test_data.append(random_str)
    dos_service = DoSService(test_data)
    dos_service._standard_opening_times = StandardOpeningTimes()
    dos_service._specififed_opening_times = []
    return dos_service
# Act
dos_service = dummy_dos_service()
nhs_kwargs = {
    "Website": dos_service.web,
    "Postcode": dos_service.postcode,
    "Phone": dos_service.publicphone,
    "OrganisationName": dos_service.publicname,
    "Address1": dos_service.address,
    "Address2": "",
    "Address3": "",
    "City": "",
    "County": "",
    "OpeningTimes": []
}
nhs_entity = NHSEntity(nhs_kwargs)
# Act
response = get_changes(dos_service, nhs_entity)
# Assert
assert {} == response, f"Should return empty dict, actually: {response}"