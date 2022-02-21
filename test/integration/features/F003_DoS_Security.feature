Feature: F003. Endpoint security and reporting

  @complete @security @smoke
  Scenario: F003S001. No api key sent to change event endpoint
    Given a Changed Event is valid
    When the Changed Event is sent for processing with "invalid" api key
    Then the change request has status code "403"

  @complete @event_sender @security
  Scenario: F003S002. No api key sent to change request endpoint
    Given a valid unsigned change request
    When the change request is sent with "invalid" api key
    Then the change request has status code "403"

