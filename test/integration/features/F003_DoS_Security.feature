Feature: F003. Endpoint security and reporting

  @complete @broken @security @pharmacy_smoke_test @pharmacy_no_log_searches
  Scenario: F003S001. No api key sent to change event endpoint
    Given a "pharmacy" Changed Event is aligned with DoS
    When the Changed Event is sent for processing with "invalid" api key
    Then the change request has status code "403"
    And the Slack channel shows an alert saying "DI Endpoint Errors"
