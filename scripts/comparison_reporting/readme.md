## **Generic Comparison Reporting**

The Reporting python class within the `reporting.py file` serve to create a generic method of comparing 2 sets of data for comparison by matching ODSCodes between them. The discrepencies are then exported as a collection of CSV files.

This is only a generic python class used to create more specific scripts in a faster simpler way.

The reporter works as follows.

```
reporter = Reporter(nhs_entities=my_nhs_entities, dos_services=my_dos_services)
reporter.run_and_save_reports(file_prefix="my_reports", output_dir="report_out/")
```

First the report is created using any 2 sets of NHS Entities and DoS Services. Then it is run by giving a file prefix name for the reports it will create, along with the desired output directory.

## **Dentist Reporting**

The `run_dentist_reports.py` script creates reports comparing Dentist NHS Entity data from an online public source, with the current DoS data found on the configured DoS Database.

This script utilises the main code base of the DI project, and such as a requirement for it to run it needs..

- Most imported modules needed in the main codebase of the project (installing from application/requirements-dev.txt should be enough, but attempting to run the program and installing packages that it says are missing should work fine.)
- The details of the chosen DoS database to use need to be available to the program in the same way they would be for the main DI project, via the enviornmental variables. The correct VPN needs to be used as would need to be to access the database in question for the machine running the script.
    - DB_REPLICA_SERVER
    - DB_PORT
    - DB_READ_ONLY_USER_NAME
    - DB_NAME
    - DB_SCHEMA
    - DB_SECRET

To run the report, from the `application/` directory run the command following command

`python3 -m comparison_reporting.run_dentist_reports`

The report will download and extract the NHS Entities from the online source, then query the DoS DB for dentists services. These will then go into the reporting python class as mentioned at the top of this readme.


## **Update Error Reporting**

The update error reporting reports attempts to find differences between the most recent changed event given by NHS UK, with the current data found in DoS.

It will use the DynamoDB database and DoS Database that it finds within the enviornmental variables at runtime.

This script utilises the main code base of the DI project, and such as a requirement for it to run it needs..

- Most imported modules needed in the main codebase of the project (installing from application/requirements-dev.txt should be enough, but attempting to run the program and installing packages that it says are missing should work fine.)
- The details of the chosen DoS database to use need to be available to the program in the same way they would be for the main DI project, via the enviornmental variables.
    - DB_REPLICA_SERVER
    - DB_PORT
    - DB_READ_ONLY_USER_NAME
    - DB_NAME
    - DB_SCHEMA
    - DB_SECRET
- The runtime enviornment will also need to be correctly authenitcated to an AWS account with access to that database. The details of the DynamoDB database that it will be using will need to be set as an enviornmental variable.
    - CHANGE_EVENTS_TABLE_NAME

To run the report, from the `application/` directory run the command following command

`python3 -m comparison_reporting.run_update_error_reports`

