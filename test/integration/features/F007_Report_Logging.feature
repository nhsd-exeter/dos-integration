Feature: F007. Report Logging

  @complete @pharmacy_cloudwatch_queries
  Scenario: F007SX01. Same dual general opening times
    Given an entry is created in the services table
    And the service is "open" on "Monday"
    And the service is "open" on "Monday"
    And the entry is committed to the services table
    When the Changed Event is sent for processing with "valid" api key
    Then the "service-matcher" lambda shows field "report_key" with value "INVALID_OPEN_TIMES"
    And "nhsuk_odscode" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "nhsuk_organisation_name" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "nhsuk_open_times_payload" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
    And "dos_services" attribute is identified in the "INVALID_OPEN_TIMES" report in "service-matcher" logs
