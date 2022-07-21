Feature: F005. Support Functions

  @complete @pharmacy_no_log_searches
  Scenario: F005S001. An unprocessed Changed Event is replayed in DI
    Given a "pharmacy" Changed Event is aligned with Dos
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI

  @complete
  Scenario: F005S002. Slack Alerting for invalid postcodes
    Given a "pharmacy" Changed Event is aligned with Dos
    And the field "Postcode" is set to "FAKE"
    When the Changed Event is sent for processing with "valid" api key
    Then the Slack channel shows an alert saying "Invalid Postcode"

  @complete @pharmacy_no_log_searches
  Scenario: F005S003 SQS Message for CE
    Given a "pharmacy" Changed Event is aligned with Dos
    And a "ce" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Change Events DLQ"

  @complete @pharmacy_no_log_searches
  Scenario: F005S004 SQS Message for CR
    Given a "cr" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Change Requests DLQ"

  @complete @pharmacy_no_log_searches
  Scenario: F005S005 SQS Message for DOS 404
    Given a "404" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Change Requests DLQ"
    And the Slack channel shows an alert saying "DI Endpoint Errors"
