Feature: F002. Invalid change event Exception handling

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S001. Unmatched DOS services exception is logged
    Given a Changed Event is valid
    And the field "ODSCode" is set to "F8KE1"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "Found 0 services in DB"
    And the Event "processor" shows field "message" with message "No matching DOS services"
    #And the Changed Event is not processed any further
    And the Event "processor" does not show "message" with message "Changes for nhs"
    And the Changed Event is not sent to Dos
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S002. Changed Event with Hidden Organisation status is reported
    Given a Changed Event is valid
    And the field "OrganisationStatus" is set to "Hidden"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "message" with message "NHS Service marked as closed or hidden"
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S003. Changed Event with Closed Organisation status is not processed
    Given a Changed Event is valid
    And the field "OrganisationStatus" is set to "Closed"
    When the Changed Event is sent for processing with "valid" api key
    #Then the Changed Event is not processed any further
    Then the Event "processor" does not show "message" with message "Changes for nhs"
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S004. A Changed Event where OrganisationTypeID is NOT PHA is reported and ignored
    Given a Changed Event is valid
    And the field "OrganisationTypeId" is set to "DEN"
    When the Changed Event is sent for processing with "valid" api key
    Then the exception is reported to cloudwatch
    #And the Changed Event is not processed any further
    And the Event "processor" does not show "message" with message "Changes for nhs"
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S005. A Changed Event where OrganisationSubType is NOT Community is reported and ignored
    Given a Changed Event is valid
    And the field "OrganisationSubType" is set to "com"
    When the Changed Event is sent for processing with "valid" api key
    Then the exception is reported to cloudwatch
    #And the Changed Event is not processed any further
    And the Event "processor" does not show "message" with message "Changes for nhs"
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S006. A Changed Event with no postcode LAT Long Values is reported
    Given a Changed Event is valid
    And the field "Postcode" is set to "BT4 2HU"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "report_key" with message "INVALID_POSTCODE"
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S007. Address changes are discarded when postcode is invalid
    Given a Changed Event is valid
    And the field "Postcode" is set to "AAAA 123"
    When the Changed Event is sent for processing with "valid" api key
    Then the 'address' from the changes is not included in the change request
    And the 'postcode' from the changes is not included in the change request
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S008. Invalid Opening Times reported where Weekday is not identified
    Given a Changed Event with the Weekday NOT present in the Opening Times data
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S009. Invalid Opening Times reported where OpeningTimeType is not defined as General or Additional
    Given a Changed Event where OpeningTimeType is NOT defined correctly
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S010. IsOpen is true AND Times is blank
    Given a Changed Event is valid
    When the OpeningTimes Opening and Closing Times data are not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S011. IsOpen is false AND Times NOT blank
    Given a Changed Event with the openingTimes IsOpen status set to false
    When the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S012. OpeningTimeType is Additional AND AdditionalOpening Date is Blank
    Given a Changed Event is valid
    When the OpeningTimes OpeningTimeType is Additional and AdditionalOpeningDate is not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S013. An OpeningTime is received for the Day or Date where IsOpen is True and IsOpen is false
    Given a Changed Event is valid
    When an AdditionalOpeningDate contains data with both true and false IsOpen status
    And the Changed Event is sent for processing with "valid" api key
    Then the OpeningTimes exception is reported to cloudwatch
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S014. All data required in the Opening times exception report is identifiable in the logs
    Given a Changed Event is valid
    When the OpeningTimes Opening and Closing Times data are not defined
    And the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs
    And the Changed Event is stored in dynamo db

@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S015. Pharmacy with overlapping opening times
    Given a Changed Event is valid
    And the Changed Event has overlapping opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the Event "processor" shows field "report_key" with message "INVALID_OPEN_TIMES"


@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S016. Pharmacy with non '13%' service type code prompts error.
    Given a Changed Event is valid
    And the field "ODSCode" is set to "TP68G"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the Event "processor" shows field "report_key" with message "UNMATCHED_SERVICE_TYPE"


@complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002S017. Pharmacies with generic bank holidays are reported in logs.
    Given a Changed Event is valid
    And the field "ODSCode" is set to "FJQ49"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the Event "processor" shows field "report_key" with message "GENERIC_BANK_HOLIDAY"


@complete @dentist_cloudwatch_queries
  Scenario: F002S018. Dentist Hidden uses correct report key
    Given a Dentist Changed Event is valid
    And the field "OrganisationStatus" is set to "Hidden"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs with report key "HIDDEN_OR_CLOSED"

@complete @dentist_cloudwatch_queries
  Scenario: F002S019. Dentist Invalid Postcode uses correct report key
    Given a Dentist Changed Event is valid
    And the field "Postcode" is set to "AAAA 123"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs with report key "INVALID_POSTCODE"

@complete @dentist_cloudwatch_queries
  Scenario: F002S020. Dentist Invalid Opening Times uses correct report key
    Given a Dentist Changed Event is valid
    And a Changed Event where OpeningTimeType is NOT defined correctly
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs with report key "INVALID_OPEN_TIMES"

@complete @dentist_cloudwatch_queries
  Scenario Outline: F002S021. Dentist Unmatched Pharmacy and Service report keys
    Given a Dentist Changed Event is valid
    And the field "ODSCode" is set to "<ods_code>"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event Processor logs with report key "<report_key>"

  Examples:
    | ods_code | report_key |
    | FQG8101  | UNMATCHED_SERVICE_TYPE |
    | V00393b  |   UNMATCHED_PHARMACY   |

@complete @dentist_cloudwatch_queries
  Scenario Outline: F002S023. Dentists with Invalid ODS Lengths.
    Given a Dentist Changed Event is valid
    And the field "ODSCode" is set to "<ods_code>"
    When the Changed Event is sent for processing with "valid" api key
    Then the Event "processor" shows field "error" with message "ODSCode Wrong Length"
    And the Event "processor" does not show "message" with message "Getting matching DoS Services for odscode"

  Examples:
    |  ods_code   |
    |   V00393    |
    |  V00393abc  |
