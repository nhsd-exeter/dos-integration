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
