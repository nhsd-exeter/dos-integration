from codecs import decode
from contextlib import closing
from io import StringIO
from re import sub

from pandas import read_csv
from requests import get


def entrypoint():
    with closing(get("https://assets.nhs.uk/data/foi/Pharmacy.csv", stream=True)) as response:
        file = decode(response.content, encoding="cp1252")
        file = file.replace("¬", "|")
        nhs_uk_data = read_csv(StringIO(file), sep="|")
        nhs_uk_data = nhs_uk_data.drop(
            columns=[
                "IsPimsManaged",
                "IsEPSEnabled",
                "Latitude",
                "Longitude",
                "ParentODSCode",
                "ParentName",
                "Email",
                "Fax",
                "Phone",
                "Website",
            ]
        )
        nhs_uk_data["Address1_Title_Case"] = nhs_uk_data["Address1"].apply(
            lambda row: set_title_case(row) if isinstance(row, str) else row
        )
        nhs_uk_data["Address2_Title_Case"] = nhs_uk_data["Address2"].apply(
            lambda row: set_title_case(row) if isinstance(row, str) else row
        )
        nhs_uk_data["Address3_Title_Case"] = nhs_uk_data["Address3"].apply(
            lambda row: set_title_case(row) if isinstance(row, str) else row
        )
        nhs_uk_data["City_Title_Case"] = nhs_uk_data["City"].apply(
            lambda row: set_title_case(row) if isinstance(row, str) else row
        )
        nhs_uk_data["County_Title_Case"] = nhs_uk_data["County"].apply(
            lambda row: set_title_case(row) if isinstance(row, str) else row
        )
        nhs_uk_data.to_csv("nhs_uk_data.csv", index=False)


def set_title_case(value: str) -> str:
    return sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda word: word.group(0).capitalize(), value)


if __name__ == "__main__":
    entrypoint()
