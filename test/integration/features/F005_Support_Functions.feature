Feature: F005. Support Functions

  @complete @pharmacy_no_log_searches
  Scenario: F005SXX1. An unprocessed Changed Event is replayed in DI
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI

  @complete @pharmacy_no_log_searches
  Scenario: F005SXX2 SQS Message for CE
    Given a basic service is created
    When a "change event dlq" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Change Events DLQ" from "SHARED_ENVIRONMENT"

  @complete @pharmacy_no_log_searches
  Scenario: F005SXX2 SQS Message for CR
    When a "update request dlq" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Update Requests DLQ" from "BLUE_GREEN_ENVIRONMENT"

  @complete @pharmacy_no_log_searches
  Scenario: F005SXX2 SQS Message for DOS 404
    When a "update request failure" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Update Requests DLQ" from "BLUE_GREEN_ENVIRONMENT"
