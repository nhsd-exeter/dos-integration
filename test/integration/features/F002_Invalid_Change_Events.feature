Feature: F002. Invalid change event Exception handling

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX1. Unmatched DOS services exception is logged
    Given a basic service is created
    And the change event "ODSCode" is set to "F8KE1"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "message" with message "Found 0 services in DB"
    And the "service-matcher" lambda shows field "message" with message "No matching DOS services"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX2. Changed Event with Hidden Organisation status is reported
    Given a basic service is created
    And the change event "OrganisationStatus" is set to "Hidden"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "message" with message "NHS Service marked as closed or hidden"
    And the service history is not updated

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX3. Changed Event with Closed Organisation status is not processed
    Given a basic service is created
    And the change event "OrganisationStatus" is set to "Closed"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with message "HIDDEN_OR_CLOSED"
    And the service history is not updated

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX4. A Changed Event where OrganisationTypeID is NOT PHA or Dentist is reported and ignored
    Given a basic service is created
    And the field "OrganisationTypeId" is set to "DEN"
    When the Changed Event is sent for processing with "valid" api key
    Then the "ingest-change-event" lambda shows field "message" with message "Validation Error - Unexpected Org Type ID: 'DEN'"
    And the service history is not updated

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX5. A Changed Event where OrganisationSubType is NOT Community is reported and ignored
    Given a basic service is created
    And the change event "OrganisationSubType" is set to "com"
    When the Changed Event is sent for processing with "valid" api key
    Then the "ingest-change-event" lambda shows field "message" with message "Validation Error - Unexpected Org Sub Type ID: 'com'"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX6. A Changed Event with no postcode LAT Long Values is reported
    Given a basic service is created
    And the change event "Postcode" is set to "BT4 2HU"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with message "INVALID_POSTCODE"

  @complete @dev @pharmacy_no_log_searches
  Scenario: F002SXX7. Address changes are discarded when postcode is invalid
    Given a basic service is created
    And the change event "Postcode" is set to "FAKE"
    And the field "Website" is set to "https://www.test.com"
    And the field "Address" is set to "FAKE2"
    When the Changed Event is sent for processing with "valid" api key
    Then the "address" has not been changed in DoS


  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX8. Invalid Opening Times reported where Weekday is not identified
    Given a basic service is created
    And the change event has no weekday present in opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with message "Opening times are not valid"
    And the Slack channel shows an alert saying "Invalid Opening Times" from "BLUE_GREEN_ENVIRONMENT"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SXX9. Invalid Opening Times reported where OpeningTimeType is not defined as General or Additional
    Given a basic service is created
    And the change event has an invalid openingtimetype
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with message "Opening times are not valid"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SX10. IsOpen is true AND Times is blank
    Given a basic service is created
    And the change event has undefined opening and closing times
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with message "Opening times are not valid"
    And the service history is not updated

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SX11. IsOpen is false AND Times NOT blank
    Given a basic service is created
    And the change event has opening times open status set to false
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with message "Opening times are not valid"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SX12. OpeningTimeType is Additional AND AdditionalOpening Date is Blank
    Given a basic service is created
    And the change event has an additional date with no specified date
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "message" with message "Opening times are not valid"

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SX15. Pharmacy with overlapping opening times
    Given a basic service is created
    And the change event "OrganisationName" is set to "Test Pharmacy"
    And the Changed Event has overlapping opening times
    When the Changed Event is sent for processing with "valid" api key
    Then the attributes for invalid opening times report is identified in the logs

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SX16. Pharmacy with non '13%' service type code prompts error.
    Given a basic service is created
    And the change event "ODSCode" is set to "TP68G"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with message "UNMATCHED_SERVICE_TYPE"
    And the service history is not updated

  @complete @dev @pharmacy_cloudwatch_queries
  Scenario: F002SX17. Pharmacies with generic bank holidays are reported in logs.
    Given a basic service is created
    And the change event "ODSCode" is set to "FJQ49"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with message "GENERIC_BANK_HOLIDAY"


  # @complete @broken @dentist_cloudwatch_queries
  # Scenario: F002S018. Dentist Hidden uses correct report key
  #   Given a "dentist" Changed Event is aligned with DoS
  #   And the field "OrganisationStatus" is set to "Hidden"
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Event "processor" shows field "report_key" with message "HIDDEN_OR_CLOSED"

  # @complete @broken @dentist_cloudwatch_queries
  # Scenario: F002S019. Dentist Invalid Postcode uses correct report key
  #   Given a "dentist" Changed Event is aligned with DoS
  #   And the field "Postcode" is set to "AAAA 123"
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Event "processor" shows field "report_key" with message "INVALID_POSTCODE"

  # @complete @broken @dentist_cloudwatch_queries
  # Scenario: F002S020. Dentist Invalid Opening Times uses correct report key
  #   Given a "dentist" Changed Event is aligned with DoS
  #   And a Changed Event where OpeningTimeType is NOT defined correctly
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Event "processor" shows field "report_key" with message "INVALID_OPEN_TIMES"

  # @complete @broken @dentist_cloudwatch_queries
  # Scenario Outline: F002S021. Dentist Unmatched Pharmacy and Service report keys
  #   Given a "dentist" Changed Event is aligned with DoS
  #   And the field "ODSCode" is set to "<ods_code>"
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the Event "processor" shows field "report_key" with message "<report_key>"

  # Examples:
  #   | ods_code | report_key             |
  #   | FQG8101  | UNMATCHED_SERVICE_TYPE |
  #   | V00393b  | UNMATCHED_PHARMACY     |

  # @complete @broken @dentist_cloudwatch_queries
  # Scenario Outline: F002S023. Dentists with Invalid ODS Lengths.
  #   Given a "dentist" Changed Event is aligned with DoS
  #   And the field "ODSCode" is set to "<ods_code>"
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the "service-sync" lambda shows field "error" with message "ODSCode Wrong Length"
  #   And the "service-matcher" lambda does not show "message" with message "Getting matching DoS Services for odscode"

  # Examples:
  #   | ods_code  |
  #   | V00393    |
  #   | V00393abc |

  # @complete @broken @dentist_cloudwatch_queries
  # Scenario Outline: F002S024. Dentist past specified opening time
  #   Given a "dentist" Changed Event is aligned with DoS
  #   And a specified opening time is set to "Jan 1 2022"
  #   When the Changed Event is sent for processing with "valid" api key
  #   Then the "service-sync" lambda shows field "message" with message "Removing Specified opening times that occur in the past"
  #   And the "service-sync" lambda shows field "all_nhs.0" with message "CLOSED on 01-01-2022"
