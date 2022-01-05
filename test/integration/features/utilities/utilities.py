import requests
import json
from os import getenv
from features.utilities.get_secrets import get_secret

url = "https://"+getenv("URL")

payload = json.dumps({
    "SearchKey": "ANEI1247",
    "ODSCode": "FC766",
    "OrganisationName": None,
    "OrganisationTypeId": "PHA",
    "OrganisationType": "Pharmacy",
    "OrganisationStatus": "Closed",
    "ServiceType": "PHA",
    "ServiceSubType": "COMPH",
    "SummaryText": "",
    "URL": "https://my-pharmacy.com/",
    "Address1": "Health Centre, Villa Park, Recreation Close, Clowne, Chesterfield, Derbyshire",
    "Address2": None,
    "Address3": None,
    "City": None,
    "County": None,
    "Latitude": 53.38030624389648,
    "Longitude": -1.4826949834823608,
    "Postcode": "NG5 2JJ",
    "Phone": "0115 9606272",
    "Email": "health.my-pharmacy@nhs.net",
    "Website": "https://new-website.com",
    "OrganisationSubType": None,
    "OrganisationAliases": [],
    "OpeningTimes": []
})


def process_change_event() -> str:
    headers = {
    'x-api-key': json.loads(get_secret())[getenv('NHS_UK_API_KEY_KEY')],
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()
