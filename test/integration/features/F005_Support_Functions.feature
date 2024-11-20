Feature: F005. Support Functions

  @complete @general
  Scenario: F005SXX1. An unprocessed Changed Event is replayed in DI
    Given a basic service is created
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI

  @complete @general
  Scenario: F005SXX1. An unprocessed Changed Event with service_type = "134" and OrganisationSubType = "DistanceSelling" is replayed in DI
    Given a basic service is created with type "134"
    And the change event "OrganisationSubType" is set to "DistanceSelling"
    When the Changed Event is sent for processing with "valid" api key
    Then the Changed Event is stored in dynamo db
    And the stored Changed Event is reprocessed in DI

  @complete @slack_and_infrastructure
  Scenario: F005SXX2 SQS Message for Change Event DLQ Alert
    Given a basic service is created
    When a "change event dlq" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Change Events DLQ" from "SHARED_ENVIRONMENT"

  @complete @slack_and_infrastructure
  Scenario Outline: F005SXX2 SQS Message DLQ Alert
    When a "<message_type>" SQS message is added to the queue
    Then the Slack channel shows an alert saying "Update Requests DLQ" from "BLUE_GREEN_ENVIRONMENT"

    Examples:
      | message_type           |
      | update request dlq     |
      | update request failure |
