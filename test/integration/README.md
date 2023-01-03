# DOS Integration Test Suite

The integration test suite is contained within test/integration and comprises a pytest suite covering various areas of the codebase. Setup is performed using the makefile in the root directory. This readme will cover at a high level the contents of the test suite and basic maintenance of it.

- [DOS Integration Test Suite](#dos-integration-test-suite)
  - [Initial Setup](#initial-setup)
  - [Running the test suite](#running-the-test-suite)
    - [Tags](#tags)
    - [Environment](#environment)
    - [Running tests](#running-tests)
  - [Adding a new test](#adding-a-new-test)
    - [Creating the Feature file entry](#creating-the-feature-file-entry)
    - [Creating a scenario](#creating-a-scenario)
    - [Creating a Given/When/Then function](#creating-a-givenwhenthen-function)
    - [Functions with no variable](#functions-with-no-variable)
    - [Functions with one or more variables](#functions-with-one-or-more-variables)
  - [Files of note when creating tests](#files-of-note-when-creating-tests)
    - [Utilities](#utilities)
    - [Generator](#generator)
    - [Dos DB Handler](#dos-db-handler)
  - [Generic Steps](#generic-steps)
    - [Given a basic service is created](#given-a-basic-service-is-created)
    - [Given an entry is created in the services table](#given-an-entry-is-created-in-the-services-table)
    - [Given the change event field is set to value](#given-the-change-event-field-is-set-to-value)
    - [When the Changed Event is sent for processing with "valid" api key](#when-the-changed-event-is-sent-for-processing-with-valid-api-key)
    - [Then the "lambda" lambda shows field "field" with message "message"](#then-the-lambda-lambda-shows-field-field-with-message-message)
    - [Then DoS has "value" in the "field" field](#then-dos-has-value-in-the-field-field)
- [Data Generation](#data-generation)
  - [Data Generation variable contents](#data-generation-variable-contents)
  - [Opening Times variable entries](#opening-times-variable-entries)
  - [Supporting Steps](#supporting-steps)
    - [the service "{field\_name}" is set to "{values}"](#the-service-field_name-is-set-to-values)
    - [the service is "{service\_status}" on "{day}"](#the-service-is-service_status-on-day)
    - [the service is "{service\_status}" on date "{date}"](#the-service-is-service_status-on-date-date)
    - [the entry is committed to the services table](#the-entry-is-committed-to-the-services-table)
  - [Context Change Event Variable](#context-change-event-variable)
  - [Notes](#notes)
    - [Contact Information](#contact-information)
    - [Opening Times](#opening-times)


## Initial Setup

The initial setup of the test suite is the same as the DoS Integration project as a whole. Please follow the setup steps contained within README.md in order to have the correct python and docker environments setup locally, as well as the correct AWS credentials. Once setup, the test suite can be run.
The test suite also requires a connection to the DoS nonprod VPN in order to validate changes made to the DOS DB.
The test suite also requires `tx-mfa` to be setup for the AWS account being used, otherwise multi-threading of tests will not function.

## Running the test suite

### Tags

The test suite is setup to be run with a series of tags, that enable the runner to choose the tests being selected. Tags do not have to match exactly, they are matched as if they are followed by a wildcard, so for example, it is possible to run all pharmacy related tests with the TAGS=pharmacy variable set, despite no tags matching pharmacy exactly. The suite does not, however, support all Cucumber tag functionality, as the tags are passed through as a variable from the run command without the '@' symbol.
E.g.
`TAGS=pharmacy`
will run the following tags:
@pharmacy_no_log_searches
@pharmacy_cloudwatch_queries
where `TAGS=pharmacy_cloudwatch_queries`
will only run the following:
@pharmacy_cloudwatch_queries

### Environment

The test suite can also be run against any environment currently setup in the nonprod AWS account. This can be selected by adding the environment name in lowercase to the ENVIRONMENT argument when running the test suite.
E.g.
If your current environment is DI-123 then you can add `ENVIRONMENT=di-123` to the run args and the test suite will run against this environment. The test environment uses "test" and the dev environment "dev".

Note: Your personal IP address may need to be white listed on the selected environment to ensure that the test can function.

### Running tests

The test suite can therefore be run by using the following command:
`make integration-test PROFILE=dev ENVIRONMENT={ENV_NAME} TAGS={TAGS}`

This will run the test suite with all selected tagged tests being run against the selected environment.

The configuration for this command can be found in the Makefile file in the root directory of the project. This will allow the retry timeout and count to be configured. This is also where ENV VARS can be setup if they need to be pulled in as part of the build process.

## Adding a new test

### Creating the Feature file entry

In order to create a new test, you will need to create the test in a feature file. There are currently 6 feature files in the test suite, though more can be added if it benefits organisation.
This feature file uses the Cucumber/Gherkin test syntax, where tests are written with a series of Given, When or Then statements. These feature files can be found at test/integration/features. Creating a new test involves adding a new scenario into one of these files, using either pre-existing test steps, or creating new ones, and then setting up the tags that the test will use.

### Creating a scenario

The scenario creation uses Pytest BDD. Documentation for this can be found [here](https://pytest-bdd.readthedocs.io/en/stable/#example)

### Creating a Given/When/Then function

If you are creating new functionality then you will need to create a new given/when/then statement in the test_steps.py file that can be found at `test/integration/steps/test_steps.py`.
This file contains a series of functions that are called when the Scenario steps are parsed. The functions in this file typically follow two formats:

### Functions with no variable

Many functions are just hard coded to perform a single task. These are setup with no input variables other than the test context and they look like this:

```@then("the Changed Event is stored in dynamo db")
def stored_dynamo_db_events_are_pulled(context: Context):
    [function code]
    return context```

There is an @tag at the beginning that will determine which type of test step calls the function. The available tags are @given @when and @then. A unique function name also needs to be determined and the context should generally be returned at the end of the function to ensure that the test context is up to date at step completion.

### Functions with one or more variables

It is also possible to have feature steps pass one or more variables through to the step function, too. This involves parsing the step text that's passed through by wrapping the readable text in a parse function. These steps look like this:

```@then(parse('the test variable is "{test_var}"'))
def test_var_function(context: Context, test_var: str):
    [function code]
    return context```

We can see that a parse has been added, as well as a value within speech marks and curly brackets. The speech marks are not required, but formatting of the test suite means we use it to denote a variable being held within. Setting a test function up like this allows you to pass a variable in. These variables are always input as a string. Multiple variables can be added to a single step.

## Files of note when creating tests

These files may be amended as part of creating tests in the test suite.

### Utilities

There are a variety of useful functions for the test suite that may be used by multiple steps, or multiple times. These are stored in the utils.py file, located at test/integration/steps/utilities/utils.py.
When creating a test, any functions should be stored here.

### Generator

There is a generator file that contains functions used for the creation of data in the DOS DB for the test suite. This also contains some functions related to the creation of the change event within the test context.

### Dos DB Handler

In some instances there may need to be some changes to the DoS DB Handler. This runs SQL queries for the test suite remotely, from a lambda function. This file can be found at application/dos_db_handler/dos_db_handler.py

## Generic Steps

These are some generic steps that are commonly used across the test suite.

### Given a basic service is created

This step creates a service in the DoS DB and sets the local context.change_event up to match the service.

### Given an entry is created in the services table

This step initilises the generator_data variable without writing out to the DOS DB. This step can be followed with steps that populate the generator_data (i.e. Given the service is "open/closed" on date "date" or Given the service "field_name" is set to "values") and then closed with a Given the entry is committed to the services table

### Given the change event field is set to value

This sets a value in the change event. This generic step should be able to change any root level value, or contacts/address data.

### When the Changed Event is sent for processing with "valid" api key

This step sends the current stored change_event to the API Gateway of the selected environment.

### Then the "lambda" lambda shows field "field" with message "message"

This is a generic log check step that will ensure a value is found in a certain field of a lambdas logs.

### Then DoS has "value" in the "field" field

This is a generic DoS check to ensure a value is found in the DoS DB services table.

# Data Generation

## Data Generation variable contents

When creating data for a test step, a variable called generator_data is created in the function a_service_table_entry_is_created in test_steps.py. This variable is a dict with the following format:
```{
        "id": A 6 digit generated numeric string,
        "uid": "test" + A 5 digit generated numeric string,
        "name": "Test Pharmacy" + a 3 digit number,
        "odscode": A 5 digit generated numeric string,
        "address": A 3 digit number followed by "Test Address",
        "town": "Nottingham",
        "postcode": "NG11GS",
        "publicphone": A randomly generated 11 digit number in string format,
        "web": "www.google.com",
    }```

It's worth noting here that all variables are in string format, regardless of whether they're a numeric value or mixed characters.

Once this variable is setup, values can be amended using a series of other test steps. New test steps can be setup to amend this value to, if the test requires it.

## Opening Times variable entries

There are 2 further keys in the data_generator dict that can be added later. These are the "specified_openings" and "standard_openings". These follow this format:
`standard_openings: [{day: "Monday", open: True, opening_time: "09:00", closing_time: "17:00"}]`
and:
`specified_openings: [{date: "25 Dec 2025", open: True, opening_time: "09:00", closing_time: "17:00"}]`

These get built in their own specified test steps, as they require separate logic in order to create the data in DOS and the change event correctly.

## Supporting Steps

### the service "{field_name}" is set to "{values}"

This step sets a variable in the data_generator variable to whatever was input. This can be used to setup custom entries for all the fields listed above. If a specific web or phone are needed, for example, or alternatively an invalid postcode, this step can be used to change the value.

### the service is "{service_status}" on "{day}"

This allows you to set the service to be open or closed on a specific day of the week. This specifically relates to general opening times, not specified opening times.

### the service is "{service_status}" on date "{date}"

This is the same as the above step, except it sets an Additional opening date rather than a general opening time.

### the entry is committed to the services table

This converts the data_generator data into a valid SQL query, and writes it to the DOS DB, saving the data to DB and also building the context.change_event to contain the same information.

## Context Change Event Variable

The context.change_event variable is structured exactly the same as a change event that gets sent into the API Gateway. It can be built from data_generator data, by passing the context through to the build_change_event() function. This can then be updated by using specified test_steps that change values within the change event.
The change event gets sent through 'as-is' when requests are sent to the API Gateway.

## Notes

### Contact Information

The contact information fields (publicphone and web) both require an update to the context.change_event variable if the CE has already been built. This is why the build_change_event_contacts function exists separately from the build change event function.

### Opening Times

The opening times data has several unique steps because of the complexity of the values that need to be set. The combinations can include openings, closures, breaks in opening and invalid values being set. This also utilises a build function to setup the change event to match the information present in the data_generator
