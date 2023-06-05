Feature: F007. Report Logging

  @complete @pharmacy_cloudwatch_queries
  Scenario: F007SX01. Check for Invalid Open Times log
    Given an entry is created in the services table
    And the service is "open" on "Monday"
    And the service is "open" on "Monday"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "INVALID_OPEN_TIMES"
    And "nhsuk_odscode" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "nhsuk_organisation_name" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "nhsuk_open_times_payload" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "dos_service_type_name" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "dos_services" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX02 Check for generic change event error log
    Given a basic service is created
    And the change event "website" is set to "test@test.com"
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-sync" lambda shows field "report_key" with value "GENERIC_CHANGE_EVENT_ERROR"
    And "ods_code" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    # And "org_type" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    # And "nhsuk_organisation_name" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    And "error_reason" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs
    And "error_info" attribute is identified in the "GENERIC_CHANGE_EVENT_ERROR" report in "service-sync" logs

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX03 Check for Incorrect Palliative Stockholder Type log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX04 Check for services with generic bank holiday openings log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX05 Check for Unexpected Pharmacy Profiling log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX06 Check for Unmatched Pharmacy Report log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX07 Check for Unmatched Service Type Report log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX08 Check for Blank Opening Times Report log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX09 Check for Hidden Or Closed Report log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries
  Scenario Outline: F007SX010 Check for Invalid Opening Times log
    Given a basic service is created

  @complete @pharmacy_cloudwatch_queries @wip
  Scenario Outline: F007SX011 Check for Invalid Postcode Report log
    Given a basic service is created
    And the change event "Postcode" is set to "FAKE"
    When the Changed Event is sent for processing with "valid" api key
    Then the Slack channel shows an alert saying "Invalid Postcode" from "BLUE_GREEN_ENVIRONMENT"
    And the "service-sync" lambda shows field "report_key" with value "INVALID_POSTCODE"
    And "nhsuk_odscode" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_organisation_name" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_address1" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_address2" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_address3" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_city" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_county" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "nhsuk_postcode" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "validation_error_reason" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
    And "dos_service" attribute is identified in the "INVALID_POSTCODE" report in "service-sync" logs
