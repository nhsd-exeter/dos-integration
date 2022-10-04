# Script to compare a dump of DI to a dump of DoS
# This version is just for comparing difference in opening times

import json
import sys
from datetime import date
from datetime import datetime as dt

import numpy as np
import pandas as pd
from dynamodb_json import json_util as dynamodb_json

if len(sys.argv) < 3:
    print("Invalid arguments : need to specify DI JSON file and a DOS specified dates CSV file to compare : ")
    print("compare_di_change_events_to_dos.py di_change_events.json dos_specified_dates.csv")
    sys.exit(2)

di_json_path = sys.argv[1]
csv_dos_path = sys.argv[2]

print("Loading files...")
di_cleaned_json = dynamodb_json.loads(
    open(
        di_json_path,
    ).read()
)
di_df = pd.DataFrame(di_cleaned_json["Items"]).set_index("ODSCode")
print("..Loaded " + di_json_path + "...")
print(di_df)
dos_df = pd.read_csv(csv_dos_path).set_index("base_odscode")
print("..Loaded " + csv_dos_path + "...")
print(dos_df)
print("...Files loaded")

print("Filtering down change events down to latest event for a given ODSCode...")
grouped_by_odscode = di_df.sort_values(["ODSCode", "SequenceNumber"], ascending=False).groupby("ODSCode")
print(grouped_by_odscode.head())
df_di_latest_events = grouped_by_odscode.first()
print("..Filtered down to latest change events")
print(df_di_latest_events)

print("Extracting NHS UK Org Type and Specified OpeningTimes from Events...")
opening_times_days = []
opening_times_specified = []
event_index = []
today_date = dt.today()
nhs_uk_type = []
for index, value in df_di_latest_events["Event"].items():
    row_opening_times_days = []
    row_opening_times_specified = {}
    for op in value["OpeningTimes"]:
        if op["Weekday"] == "":
            if dt.strptime(op["AdditionalOpeningDate"], "%b %d %Y") >= today_date:
                # Formatting Specified Opening so they can be easily compared with DoS
                sp = {
                    "date": dt.strptime(op["AdditionalOpeningDate"], "%b %d %Y").strftime("%Y-%m-%d"),
                    "starttime": "00:00:00" if not op["OpeningTime"] else op["OpeningTime"] + ":00",
                    "endtime": "00:00:00" if not op["ClosingTime"] else op["ClosingTime"] + ":00",
                    "isclosed": (op["IsOpen"] == False),
                }
                row_opening_times_specified[sp["date"]] = sp
        else:
            row_opening_times_days.append(op)
    opening_times_days.append(row_opening_times_days)
    opening_times_specified.append(row_opening_times_specified if len(row_opening_times_specified) > 0 else None)
    nhs_uk_type.append(value["OrganisationSubType"])
    event_index.append(index)
df_di_latest_events = df_di_latest_events.join(
    pd.Series(opening_times_days, index=event_index, name="OpeningTimeWeekdays")
)
df_di_latest_events = df_di_latest_events.join(
    pd.Series(opening_times_specified, index=event_index, name="OpeningTimeSpecified")
)
df_di_latest_events = df_di_latest_events.join(pd.Series(nhs_uk_type, index=event_index, name="NhsUkType"))
df_di_latest_specified_openings = df_di_latest_events.drop(
    columns=["Event", "SequenceNumber", "EventReceived", "TTL", "Id", "OpeningTimeWeekdays"]
)
df_di_latest_specified_openings.index.names = ["base_odscode"]
print("..Finished extracting fields from Events")
print(df_di_latest_specified_openings)
print(df_di_latest_specified_openings.columns)

print("Remove past specified dates and unused fields from DoS Extract..")
specified_openings = []
sp_idx = []
for index, value in dos_df["specified_openings"].items():
    sp = json.loads(value)
    sp_future = {}
    for item in sp:
        if dt.strptime(item["date"], "%Y-%m-%d") >= today_date:
            sp_future[item["date"]] = item
    specified_openings.append(sp_future if len(sp_future) > 0 else None)
    sp_idx.append(index)
dos_df = dos_df.drop(columns=["specified_openings"])
dos_df = dos_df.join(pd.Series(specified_openings, index=sp_idx, name="specified_openings"))
dos_df_slim = dos_df.drop(columns=["id", "odscode"])
print("..Finished removing dates and fields")
print(dos_df_slim)
print(dos_df_slim.columns)

print("Aligning and comparing NHS UK with DoS specified dates..")
joined = df_di_latest_specified_openings.join(dos_df_slim)
joined["sp_aligned"] = np.where(joined["OpeningTimeSpecified"] == joined["specified_openings"], True, False)
joined = joined.drop_duplicates(subset=["uid"], keep="first")
print(joined)
filtered_joined = joined.loc[joined["sp_aligned"] == False]
print(filtered_joined)
print("..Finished aligning and comparing")
save_filename = "live-di-dos-sp-compare-" + dt.today().strftime("%Y%m%d-%H%M") + ".csv"
print("Save comparison to file " + save_filename)
joined.to_csv(save_filename)
