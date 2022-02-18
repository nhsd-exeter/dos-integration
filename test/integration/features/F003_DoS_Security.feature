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

  @complete @event_sender @security
  Scenario: F003S003. An unsigned valid change request sent to event sender
    Given a valid unsigned change request
    When the change request is sent with "valid" api key
    Then the change request has status code "400"

  @complete @event_sender
  Scenario: F003S004. An signed valid change request sent to event sender
    Given a valid unsigned change request
    And change request has valid signature
    When the change request is sent with "valid" api key
    Then the change request has status code "201"

  @complete @event_sender @security
  Scenario: F003S005. An signed valid change request sent to event sender with invalid signature
    Given a valid unsigned change request
    And change request has invalid signature
    When the change request is sent with "valid" api key
    Then the change request has status code "400"

  @complete @event_sender @security
  Scenario: F003S006. An signed valid change request sent to event sender with expired signature
    Given a valid unsigned change request
    And change request has expired signature
    When the change request is sent with "valid" api key
    Then the change request has status code "400"
