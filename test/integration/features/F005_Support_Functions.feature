Feature: F005. Support Functions

  @complete @pharmacy_no_log_searches
  Scenario: F005SXX1. An unprocessed Changed Event is replayed in DI
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI

@complete @pharmacy_no_log_searches
  Scenario: F005SXX2. Slack Alerting for invalid postcodes
    Given a basic service is created
    And the change event "Postcode" is set to "FAKE"
    When the Changed Event is sent for processing with "valid" api key
    Then the Slack channel shows an alert saying "Invalid Postcode" from "BLUE_GREEN_ENVIRONMENT"

  #Tests to be enabled in DI-533
  @complete @broken @pharmacy_no_log_searches
  Scenario: F005SXX3 SQS Message for CE
    Given a basic service is created
    When a "change event dlq" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Change Events DLQ" from "SHARED_ENVIRONMENT"

  @complete @broken @pharmacy_no_log_searches
  Scenario: F005SXX4 SQS Message for CR
    When a "update request dlq" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Update Requests DLQ" from "BLUE_GREEN_ENVIRONMENT"

  @complete @broken @pharmacy_no_log_searches
  Scenario: F005SXX5 SQS Message for DOS 404
    When a "update request failure" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Update Requests DLQ" from "BLUE_GREEN_ENVIRONMENT"
