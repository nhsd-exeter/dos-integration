Feature: F003. Endpoint security and reporting

  @complete @security @smoke @no_log_searches
  Scenario: F003S001. No api key sent to change event endpoint
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "invalid" api key
    Then the change request has status code "403"
